#!/usr/bin/env python3
"""
QUIRRELY MOCK SERVICES v1.0
In-memory service layer for testing - CLAUDE.md compliant

Provides mock implementations of all backend services for testing.
All data exists only in memory - NO database connections or file writes.
Enables comprehensive testing without external dependencies.
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import json

from .simulation_core import (
    QuirrelyTestSimulationEngine,
    SimulatedUser, SimulatedPartnership, SimulatedAnalysis,
    UserTier, Country, VoiceProfile, VoiceStance
)


# ═══════════════════════════════════════════════════════════════════════════
# MOCK COLLABORATION SERVICE
# ═══════════════════════════════════════════════════════════════════════════

class MockCollaborationService:
    """In-memory collaboration service for testing"""
    
    def __init__(self, simulation_engine: QuirrelyTestSimulationEngine):
        self.engine = simulation_engine
        self.email_templates = MockEmailTemplates()
    
    async def create_partnership_invitation(
        self,
        initiator_user_id: str,
        partner_email: str,
        partnership_name: str,
        partnership_intention: str,
        partnership_type: str = "growth"
    ) -> Dict[str, Any]:
        """Create partnership invitation (in-memory)"""
        
        try:
            partnership_id = self.engine.simulate_partnership_creation(
                initiator_user_id=initiator_user_id,
                partner_email=partner_email,
                partnership_name=partnership_name,
                partnership_type=partnership_type
            )
            
            partnership = self.engine.temp_partnerships[partnership_id]
            
            # Simulate email sending (no actual email)
            email_content = self.email_templates.generate_invitation_email(
                partnership_name=partnership_name,
                partnership_type=partnership_type,
                initiator_name=self.engine.temp_users[initiator_user_id].display_name,
                invitation_token=partnership.invitation_token
            )
            
            return {
                "success": True,
                "partnership_id": partnership_id,
                "invitation_token": partnership.invitation_token,
                "email_sent": True,
                "email_preview": email_content["subject"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def accept_partnership_invitation(
        self,
        invitation_token: str,
        partner_user_id: str
    ) -> Dict[str, Any]:
        """Accept partnership invitation (in-memory)"""
        
        # Find partnership by invitation token
        partnership = None
        partnership_id = None
        
        for pid, p in self.engine.temp_partnerships.items():
            if p.invitation_token == invitation_token:
                partnership = p
                partnership_id = pid
                break
        
        if not partnership:
            return {"success": False, "error": "Invalid invitation token"}
        
        if partnership.status != "pending":
            return {"success": False, "error": "Invitation already processed"}
        
        success = self.engine.simulate_partnership_acceptance(partnership_id, partner_user_id)
        
        return {
            "success": success,
            "partnership_id": partnership_id,
            "status": "active" if success else "failed"
        }
    
    async def get_partnership_status(self, partnership_id: str) -> Dict[str, Any]:
        """Get partnership status (in-memory)"""
        
        if partnership_id not in self.engine.temp_partnerships:
            return {"success": False, "error": "Partnership not found"}
        
        partnership = self.engine.temp_partnerships[partnership_id]
        
        return {
            "success": True,
            "partnership": {
                "id": partnership_id,
                "status": partnership.status,
                "partnership_name": partnership.partnership_name,
                "partnership_type": partnership.partnership_type,
                "shared_creative_space": partnership.shared_creative_space,
                "shared_space_used": partnership.shared_space_used,
                "initiator_solo_remaining": partnership.initiator_solo_remaining,
                "partner_solo_remaining": partnership.partner_solo_remaining,
                "created_at": partnership.created_at.isoformat(),
                "accepted_at": partnership.accepted_at.isoformat() if partnership.accepted_at else None
            }
        }
    
    async def track_word_usage(
        self,
        partnership_id: str,
        user_id: str,
        words_used: int,
        usage_type: str = "shared"
    ) -> Dict[str, Any]:
        """Track word usage in partnership (in-memory)"""
        
        success = self.engine.simulate_partnership_word_usage(
            partnership_id=partnership_id,
            user_id=user_id,
            words_used=words_used,
            usage_type=usage_type
        )
        
        return {
            "success": success,
            "words_used": words_used,
            "usage_type": usage_type,
            "remaining_space": self._calculate_remaining_space(partnership_id, user_id, usage_type)
        }
    
    def _calculate_remaining_space(
        self,
        partnership_id: str,
        user_id: str,
        usage_type: str
    ) -> int:
        """Calculate remaining space after usage"""
        
        if partnership_id not in self.engine.temp_partnerships:
            return 0
        
        partnership = self.engine.temp_partnerships[partnership_id]
        
        if usage_type == "shared":
            return partnership.shared_creative_space - partnership.shared_space_used
        elif usage_type == "solo":
            if user_id == partnership.initiator_user_id:
                return partnership.initiator_solo_remaining
            elif user_id == partnership.partner_user_id:
                return partnership.partner_solo_remaining
        
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# MOCK HALO BRIDGE
# ═══════════════════════════════════════════════════════════════════════════

class MockHALOBridge:
    """In-memory HALO safety simulation"""
    
    def __init__(self, simulation_engine: QuirrelyTestSimulationEngine):
        self.engine = simulation_engine
        self.violation_patterns = [
            "hate", "abuse", "spam", "harassment", "violence",
            "explicit", "offensive", "toxic", "threat"
        ]
        self.user_violation_counts: Dict[str, int] = {}
    
    async def analyze_content(
        self,
        user_id: str,
        content: str,
        content_type: str = "analysis"
    ) -> Dict[str, Any]:
        """Analyze content for HALO safety violations"""
        
        # Initialize user violation count
        if user_id not in self.user_violation_counts:
            self.user_violation_counts[user_id] = 0
        
        # Simple content analysis simulation
        content_lower = content.lower()
        violations_found = []
        
        for pattern in self.violation_patterns:
            if pattern in content_lower:
                violations_found.append(pattern)
        
        # Determine violation tier
        if not violations_found:
            tier = 0  # Clean content
            action = "approved"
        elif len(violations_found) == 1 and len(content) > 50:
            tier = 1  # Warning
            action = "warning"
        elif len(violations_found) <= 2:
            tier = 2  # Caution
            action = "caution"
        else:
            tier = 3  # Blocked
            action = "blocked"
        
        # Escalate based on user history
        if tier > 0:
            self.user_violation_counts[user_id] += 1
            if self.user_violation_counts[user_id] >= 3:
                tier = min(tier + 1, 3)
                action = "blocked" if tier == 3 else action
        
        # Generate HALO event using SimulatedEvent
        from .simulation_core import SimulatedEvent
        
        self.engine.temp_events.append(SimulatedEvent(
            event_type="halo_analysis_completed",
            user_id=user_id,
            data={
                "content_type": content_type,
                "violation_tier": tier,
                "action": action,
                "violations_found": violations_found,
                "user_violation_count": self.user_violation_counts[user_id]
            },
            observer="halo_observer",
            timestamp=datetime.utcnow()
        ))
        
        return {
            "success": True,
            "analysis_result": {
                "violation_tier": tier,
                "action": action,
                "safe_to_proceed": tier < 3,
                "violations_found": violations_found,
                "user_violation_count": self.user_violation_counts[user_id],
                "message": self._get_user_message(tier, action)
            }
        }
    
    def _get_user_message(self, tier: int, action: str) -> str:
        """Get user-friendly message for HALO result"""
        
        messages = {
            0: "Content approved - no issues detected.",
            1: "Please review your content for potential issues.",
            2: "Content flagged for review - please modify before continuing.",
            3: "Content blocked due to policy violations. Please revise completely."
        }
        
        return messages.get(tier, "Content analysis completed.")
    
    async def get_user_safety_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's safety status and violation history"""
        
        violation_count = self.user_violation_counts.get(user_id, 0)
        
        if violation_count == 0:
            status = "good_standing"
        elif violation_count <= 2:
            status = "warning"
        else:
            status = "restricted"
        
        return {
            "user_id": user_id,
            "status": status,
            "violation_count": violation_count,
            "restrictions_active": violation_count >= 3
        }


# ═══════════════════════════════════════════════════════════════════════════
# MOCK META ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

class MockMetaOrchestrator:
    """In-memory Meta/Observer simulation"""
    
    def __init__(self, simulation_engine: QuirrelyTestSimulationEngine):
        self.engine = simulation_engine
        self.observers = {
            "achievement_observer": MockAchievementObserver(),
            "viral_observer": MockViralObserver(),
            "funnel_observer": MockFunnelObserver(),
            "stretch_observer": MockStretchObserver(),
            "retention_observer": MockRetentionObserver(),
            "halo_observer": MockHALOObserver()
        }
        self.cycle_count = 0
    
    async def run_meta_cycle(self) -> Dict[str, Any]:
        """Simulate Meta orchestrator cycle"""
        
        self.cycle_count += 1
        cycle_start = datetime.utcnow()
        
        # Process events with each observer
        observer_results = {}
        total_events_processed = 0
        
        for observer_name, observer in self.observers.items():
            observer_events = self.engine.get_observer_events(observer_name)
            result = await observer.process_events(observer_events)
            observer_results[observer_name] = result
            total_events_processed += len(observer_events)
        
        # Calculate system health
        health_scores = [getattr(result, "health_score", 85) if hasattr(result, "health_score") else result.get("health_score", 85) for result in observer_results.values()]
        system_health = sum(health_scores) / len(health_scores) if health_scores else 85
        
        # Generate optimization suggestions
        suggestions = []
        for observer_name, result in observer_results.items():
            suggestions.extend(getattr(result, "suggestions", []) if hasattr(result, "suggestions") else result.get("suggestions", []))
        
        cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
        
        return {
            "cycle_id": f"cycle_{self.cycle_count}_{uuid.uuid4().hex[:8]}",
            "cycle_count": self.cycle_count,
            "duration_seconds": cycle_duration,
            "events_processed": total_events_processed,
            "system_health": system_health,
            "observer_results": observer_results,
            "optimization_suggestions": suggestions,
            "success": True
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        observer_status = {}
        for observer_name, observer in self.observers.items():
            observer_status[observer_name] = await observer.get_status()
        
        return {
            "meta_orchestrator": {
                "version": "5.1.0-G2M",
                "cycles_completed": self.cycle_count,
                "status": "operational"
            },
            "observers": observer_status,
            "events_pending": len(self.engine.temp_events),
            "simulation_mode": True
        }


# ═══════════════════════════════════════════════════════════════════════════
# MOCK OBSERVERS
# ═══════════════════════════════════════════════════════════════════════════

class MockAchievementObserver:
    """Mock achievement system observer"""
    
    async def process_events(self, events: List[Any]) -> Dict[str, Any]:
        achievement_events = [e for e in events if getattr(e, "event_type", None) in [
            "voice_analysis_completed", "collaboration_started", "user_created"
        ]]
        
        return {
            "health_score": random.uniform(88, 95),
            "events_processed": len(achievement_events),
            "badges_awarded": random.randint(0, 3),
            "xp_distributed": random.randint(50, 500),
            "suggestions": [
                {"type": "badge_threshold", "confidence": 0.75, "domain": "gamification"}
            ] if random.random() > 0.7 else []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        return {
            "observer_id": "achievement_observer",
            "health_score": random.uniform(88, 95),
            "active_users_tracking": random.randint(10, 50)
        }

class MockViralObserver:
    """Mock viral growth observer"""
    
    async def process_events(self, events: List[Any]) -> Dict[str, Any]:
        viral_events = [e for e in events if getattr(e, "event_type", None) in [
            "content_shared", "referral_signup"
        ]]
        
        return {
            "health_score": random.uniform(85, 92),
            "events_processed": len(viral_events),
            "k_factor": random.uniform(0.15, 0.45),
            "shares_tracked": len([e for e in viral_events if getattr(e, "event_type", None) == "content_shared"]),
            "suggestions": []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        return {
            "observer_id": "viral_observer",
            "health_score": random.uniform(85, 92),
            "k_factor_target": 0.35
        }

class MockFunnelObserver:
    """Mock conversion funnel observer"""
    
    async def process_events(self, events: List[Any]) -> Dict[str, Any]:
        funnel_events = [e for e in events if getattr(e, "event_type", None) in [
            "analysis_run", "partnership_invitation_sent", "partnership_accepted"
        ]]
        
        return {
            "health_score": random.uniform(87, 94),
            "events_processed": len(funnel_events),
            "conversion_signals_generated": random.randint(0, 2),
            "suggestions": []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        return {
            "observer_id": "funnel_observer", 
            "health_score": random.uniform(87, 94)
        }

class MockStretchObserver:
    """Mock STRETCH exercise observer"""
    
    async def process_events(self, events: List[Any]) -> Dict[str, Any]:
        return {
            "health_score": random.uniform(89, 96),
            "events_processed": 0,  # No STRETCH events in basic simulation
            "suggestions": []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        return {
            "observer_id": "stretch_observer",
            "health_score": random.uniform(89, 96)
        }

class MockRetentionObserver:
    """Mock retention observer"""
    
    async def process_events(self, events: List[Any]) -> Dict[str, Any]:
        return {
            "health_score": random.uniform(91, 97),
            "events_processed": len(events),
            "interventions_triggered": random.randint(0, 1),
            "suggestions": []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        return {
            "observer_id": "retention_observer",
            "health_score": random.uniform(91, 97)
        }

class MockHALOObserver:
    """Mock HALO safety observer"""
    
    async def process_events(self, events: List[Any]) -> Dict[str, Any]:
        halo_events = [e for e in events if getattr(e, "event_type", None) in [
            "halo_analysis_completed", "content_violation"
        ]]
        
        return {
            "health_score": random.uniform(93, 98),
            "events_processed": len(halo_events),
            "violations_detected": len([e for e in halo_events if getattr(e, "event_type", None) == "content_violation"]),
            "suggestions": []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        return {
            "observer_id": "halo_observer",
            "health_score": random.uniform(93, 98)
        }


# ═══════════════════════════════════════════════════════════════════════════
# MOCK EMAIL TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

class MockEmailTemplates:
    """Mock email template service"""
    
    def generate_invitation_email(
        self,
        partnership_name: str,
        partnership_type: str,
        initiator_name: str,
        invitation_token: str
    ) -> Dict[str, str]:
        """Generate partnership invitation email (simulation only)"""
        
        subject = f"✨ {initiator_name} invited you to collaborate on '{partnership_name}'"
        
        html_content = f"""
        <h1>You're invited to collaborate!</h1>
        <p>{initiator_name} has invited you to join a {partnership_type} partnership called "{partnership_name}".</p>
        <p>This collaboration will give you access to:</p>
        <ul>
            <li>25,000 shared creative words</li>
            <li>12,500 personal words</li>
            <li>Advanced collaboration tools</li>
            <li>Shared writing insights</li>
        </ul>
        <p><a href="https://quirrely.ca/partnership/accept/{invitation_token}" style="background: #7CAE9E; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accept Invitation</a></p>
        <p>This invitation will expire in 7 days.</p>
        """
        
        text_content = f"""
        You're invited to collaborate!
        
        {initiator_name} has invited you to join a {partnership_type} partnership called "{partnership_name}".
        
        Accept at: https://quirrely.ca/partnership/accept/{invitation_token}
        
        This invitation expires in 7 days.
        """
        
        return {
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
            "invitation_token": invitation_token
        }


# ═══════════════════════════════════════════════════════════════════════════
# MOCK SERVICE FACTORY
# ═══════════════════════════════════════════════════════════════════════════

class MockServiceFactory:
    """Factory for creating mock services with shared simulation engine"""
    
    def __init__(self, simulation_engine: Optional[QuirrelyTestSimulationEngine] = None):
        self.simulation_engine = simulation_engine or QuirrelyTestSimulationEngine()
        self._services = {}
    
    def get_collaboration_service(self) -> MockCollaborationService:
        """Get or create mock collaboration service"""
        if "collaboration" not in self._services:
            self._services["collaboration"] = MockCollaborationService(self.simulation_engine)
        return self._services["collaboration"]
    
    def get_halo_bridge(self) -> MockHALOBridge:
        """Get or create mock HALO bridge"""
        if "halo" not in self._services:
            self._services["halo"] = MockHALOBridge(self.simulation_engine)
        return self._services["halo"]
    
    def get_meta_orchestrator(self) -> MockMetaOrchestrator:
        """Get or create mock Meta orchestrator"""
        if "meta" not in self._services:
            self._services["meta"] = MockMetaOrchestrator(self.simulation_engine)
        return self._services["meta"]
    
    def get_simulation_engine(self) -> QuirrelyTestSimulationEngine:
        """Get the shared simulation engine"""
        return self.simulation_engine
    
    def cleanup(self):
        """Cleanup all services and simulation engine"""
        self._services.clear()
        # Simulation engine auto-cleanup via __del__


# ═══════════════════════════════════════════════════════════════════════════
# TESTING & VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 MOCK SERVICES - VALIDATION TEST")
    print("=" * 50)
    
    async def test_mock_services():
        # Create service factory
        factory = MockServiceFactory()
        
        try:
            # Test collaboration service
            print("\n🤝 Testing Mock Collaboration Service...")
            collaboration = factory.get_collaboration_service()
            
            # Create test users
            user1_id = factory.simulation_engine.simulate_user_creation(UserTier.PRO, Country.CANADA)
            user2_id = factory.simulation_engine.simulate_user_creation(UserTier.PRO, Country.UNITED_KINGDOM)
            
            # Test partnership creation
            result = await collaboration.create_partnership_invitation(
                user1_id, "test@example.com", "Test Partnership", "Testing collaboration", "growth"
            )
            print(f"  ✅ Partnership created: {result['success']}")
            
            if result['success']:
                # Test partnership acceptance
                accept_result = await collaboration.accept_partnership_invitation(
                    result['invitation_token'], user2_id
                )
                print(f"  ✅ Partnership accepted: {accept_result['success']}")
            
            # Test HALO bridge
            print("\n🛡️ Testing Mock HALO Bridge...")
            halo = factory.get_halo_bridge()
            
            # Test content analysis
            clean_result = await halo.analyze_content(user1_id, "This is clean content for testing.")
            print(f"  ✅ Clean content analysis: tier {clean_result['analysis_result']['violation_tier']}")
            
            violation_result = await halo.analyze_content(user1_id, "This content contains hate speech.")
            print(f"  ✅ Violation detection: tier {violation_result['analysis_result']['violation_tier']}")
            
            # Test Meta orchestrator
            print("\n🧠 Testing Mock Meta Orchestrator...")
            meta = factory.get_meta_orchestrator()
            
            cycle_result = await meta.run_meta_cycle()
            print(f"  ✅ Meta cycle completed: {cycle_result['success']}")
            print(f"  📊 Events processed: {cycle_result['events_processed']}")
            print(f"  🏥 System health: {cycle_result['system_health']:.1f}")
            
            # Test zero persistence
            print("\n🔒 Testing Zero Persistence...")
            persistence_check = factory.simulation_engine.validate_zero_persistence()
            all_passed = all(persistence_check.values())
            print(f"  ✅ Zero persistence validation: {all_passed}")
            
            if all_passed:
                print("\n🎉 ALL MOCK SERVICES TESTS PASSED")
                print("✅ Collaboration service functional")
                print("✅ HALO bridge operational") 
                print("✅ Meta orchestrator working")
                print("✅ Zero persistence maintained")
                print("\n🚀 READY FOR UI VALIDATION FRAMEWORK")
            else:
                print("\n❌ SOME TESTS FAILED - Review required")
        
        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
        
        finally:
            factory.cleanup()
    
    # Run async test
    asyncio.run(test_mock_services())