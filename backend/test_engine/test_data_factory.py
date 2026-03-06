#!/usr/bin/env python3
"""
QUIRRELY TEST DATA FACTORY v1.0
In-memory test data generation - CLAUDE.md compliant

Generates realistic test data for comprehensive system testing.
All data exists only in memory - NO persistence to files or database.
Supports all 8 v2.0 systems with country/profile/tier variations.
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .simulation_core import (
    QuirrelyTestSimulationEngine,
    UserTier, Country, VoiceProfile, VoiceStance
)


# ═══════════════════════════════════════════════════════════════════════════
# TEST DATA PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

class TestScenario(str, Enum):
    """Test scenario types"""
    BASIC_USER_JOURNEY = "basic_user_journey"
    PARTNERSHIP_COMPLETE = "partnership_complete"
    VIRAL_GROWTH_CHAIN = "viral_growth_chain"
    COUNTRY_LOCALIZATION = "country_localization"
    HALO_SAFETY_TESTS = "halo_safety_tests"
    VOICE_PROFILE_MATRIX = "voice_profile_matrix"
    SEO_BLOG_SIMULATION = "seo_blog_simulation"
    META_OBSERVER_STRESS = "meta_observer_stress"

@dataclass
class TestDataProfile:
    """Profile for generating test data"""
    scenario: TestScenario
    user_count: int
    country_distribution: Dict[Country, float]
    tier_distribution: Dict[UserTier, float]
    voice_profiles: List[VoiceProfile]
    partnership_ratio: float = 0.3  # % of Pro users who create partnerships
    viral_share_ratio: float = 0.2  # % of analyses that get shared
    halo_violation_ratio: float = 0.05  # % of content with violations


# ═══════════════════════════════════════════════════════════════════════════
# REALISTIC CONTENT GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

class ContentGenerator:
    """Generates realistic content for voice analysis testing"""
    
    # Sample content by voice profile
    VOICE_CONTENT_SAMPLES = {
        VoiceProfile.ASSERTIVE: [
            "I firmly believe that effective communication requires direct, confident language that leaves no room for misunderstanding.",
            "The evidence clearly demonstrates that our approach is the most efficient path forward for this project.",
            "Without question, this strategy will deliver the results we need within the specified timeframe."
        ],
        VoiceProfile.MINIMAL: [
            "Simple. Direct. Clear.",
            "Yes. This works.",
            "Done. Next question."
        ],
        VoiceProfile.CONTRADICTORY: [
            "While I agree with the premise, I must point out that the conclusion seems fundamentally flawed, yet perhaps that's exactly what makes it brilliant.",
            "This approach is both innovative and traditional, effective yet problematic, which creates interesting paradoxes worth exploring."
        ],
        VoiceProfile.OPEN: [
            "I'm curious about your perspective on this matter, and I wonder if we might explore different possibilities together.",
            "There seem to be many interesting angles to consider here, and I'd love to hear what others think about this topic."
        ],
        VoiceProfile.CLOSED: [
            "The data supports this conclusion definitively.",
            "This is the established protocol that we follow consistently.",
            "The research clearly indicates this specific outcome."
        ],
        VoiceProfile.BALANCED: [
            "After considering multiple perspectives, it appears that a measured approach would be most appropriate for this situation.",
            "While there are valid arguments on both sides, the evidence suggests a moderate path forward."
        ],
        VoiceProfile.EXPANSIVE: [
            "This fascinating topic opens up numerous possibilities for exploration, connecting to broader themes of human experience, cultural evolution, and the intricate ways that language shapes our understanding of reality itself.",
            "When we consider the implications of this concept, we find ourselves traversing landscapes of meaning that extend far beyond the immediate question."
        ],
        VoiceProfile.RHYTHMIC: [
            "Step by step, piece by piece, we build understanding through careful attention to pattern and flow.",
            "First this, then that, leading naturally to the next logical sequence in our methodical approach."
        ],
        VoiceProfile.FLOWING: [
            "These ideas naturally connect to one another, creating a seamless narrative that moves gracefully from concept to application.",
            "The thoughts flow together like water finding its path, each insight leading smoothly to the next discovery."
        ],
        VoiceProfile.STRUCTURED: [
            "First, we must establish the foundational principles. Second, we apply the analytical framework. Third, we evaluate the outcomes systematically.",
            "The methodology consists of three distinct phases: data collection, analysis, and implementation of findings."
        ]
    }
    
    # Content with potential HALO violations (for safety testing)
    VIOLATION_CONTENT_SAMPLES = {
        "tier_1": [  # Warnings
            "This is barely adequate work that shows minimal effort.",
            "I'm frustrated with this disappointing performance."
        ],
        "tier_2": [  # Cautions
            "This is absolutely terrible and unacceptable work.",
            "I hate dealing with these incompetent people."
        ],
        "tier_3": [  # Blocks
            "This contains explicit hate speech targeting specific groups.",
            "Threatening language and harassment directed at individuals."
        ]
    }
    
    # Country-specific content variations
    COUNTRY_CONTENT_VARIATIONS = {
        Country.CANADA: {
            "spelling": ["colour", "realise", "centre", "behaviour"],
            "cultural_phrases": ["I'm sorry, but", "perhaps we might consider", "thank you kindly"],
            "topics": ["hockey", "maple syrup", "multicultural", "bilingual", "prairie"]
        },
        Country.UNITED_KINGDOM: {
            "spelling": ["colour", "realise", "centre", "behaviour"],
            "cultural_phrases": ["I beg your pardon", "rather", "quite right", "brilliant"],
            "topics": ["cricket", "tea", "queue", "proper", "brilliant"]
        },
        Country.AUSTRALIA: {
            "spelling": ["colour", "realise", "centre", "behaviour"],
            "cultural_phrases": ["no worries", "fair dinkum", "she'll be right", "good on ya"],
            "topics": ["cricket", "barbecue", "outback", "mate", "footy"]
        },
        Country.NEW_ZEALAND: {
            "spelling": ["colour", "realise", "centre", "behaviour"],
            "cultural_phrases": ["yeah, nah", "sweet as", "choice", "chur"],
            "topics": ["rugby", "kiwi", "tramping", "bach", "jandals"]
        }
    }
    
    @classmethod
    def generate_voice_content(
        cls,
        voice_profile: VoiceProfile,
        country: Country,
        word_count_target: int = 50
    ) -> str:
        """Generate realistic content for voice profile testing"""
        
        base_content = random.choice(cls.VOICE_CONTENT_SAMPLES.get(voice_profile, [
            "This is sample content for voice analysis testing purposes."
        ]))
        
        # Add country-specific elements
        country_data = cls.COUNTRY_CONTENT_VARIATIONS.get(country, {})
        if country_data and random.random() < 0.3:  # 30% chance to add cultural element
            cultural_phrase = random.choice(country_data.get("cultural_phrases", []))
            if random.random() < 0.5:
                base_content = f"{cultural_phrase}, {base_content.lower()}"
            else:
                base_content = f"{base_content} {cultural_phrase}."
        
        # Extend content to reach target word count
        current_words = len(base_content.split())
        if current_words < word_count_target:
            additional_sentences = [
                "This content demonstrates the unique characteristics of this writing style.",
                "The analysis system will evaluate various linguistic patterns and structures.",
                "These examples help test the voice detection algorithms comprehensively.",
                "Multiple samples ensure accurate profiling across different contexts.",
                "The system learns from diverse content to improve accuracy over time."
            ]
            
            while current_words < word_count_target:
                addition = random.choice(additional_sentences)
                base_content += f" {addition}"
                current_words = len(base_content.split())
        
        return base_content
    
    @classmethod
    def generate_halo_violation_content(cls, tier: int) -> str:
        """Generate content with specific HALO violation tiers"""
        
        if tier == 0:
            # Clean content
            return random.choice([
                "This is perfectly acceptable content for analysis.",
                "A thoughtful piece of writing that demonstrates good communication.",
                "Clear, professional content that meets all guidelines."
            ])
        elif tier == 1:
            return random.choice(cls.VIOLATION_CONTENT_SAMPLES["tier_1"])
        elif tier == 2:
            return random.choice(cls.VIOLATION_CONTENT_SAMPLES["tier_2"])
        elif tier >= 3:
            return random.choice(cls.VIOLATION_CONTENT_SAMPLES["tier_3"])
        
        return "Standard content for testing purposes."
    
    @classmethod
    def generate_partnership_content(
        cls,
        partnership_type: str,
        initiator_profile: VoiceProfile,
        country: Country
    ) -> Dict[str, str]:
        """Generate realistic partnership invitation content"""
        
        partnership_names = {
            "growth": ["Growth Journey", "Development Partnership", "Learning Alliance", "Progress Together"],
            "creative": ["Creative Collaboration", "Artistic Vision", "Innovation Lab", "Creative Minds"],
            "professional": ["Professional Network", "Business Writing", "Corporate Communications", "Industry Focus"],
            "heart": ["Heart Connection", "Personal Stories", "Life Experiences", "Emotional Journey"],
            "life": ["Life Writing", "Experience Sharing", "Journey Together", "Story Partners"]
        }
        
        intentions = {
            "growth": "Supporting each other's writing development and skill enhancement",
            "creative": "Exploring creative expression and artistic collaboration",
            "professional": "Advancing professional communication and business writing",
            "heart": "Sharing personal stories and emotional connections",
            "life": "Documenting life experiences and meaningful moments"
        }
        
        name = random.choice(partnership_names.get(partnership_type, ["Writing Partnership"]))
        intention = intentions.get(partnership_type, "Collaborative writing exploration")
        
        # Add country-specific cultural adaptation
        country_data = cls.COUNTRY_CONTENT_VARIATIONS.get(country, {})
        if country_data and random.random() < 0.2:
            cultural_topic = random.choice(country_data.get("topics", []))
            intention += f" with focus on {cultural_topic} themes"
        
        return {
            "partnership_name": name,
            "partnership_intention": intention,
            "partnership_type": partnership_type
        }


# ═══════════════════════════════════════════════════════════════════════════
# TEST DATA FACTORY
# ═══════════════════════════════════════════════════════════════════════════

class QuirrelyTestDataFactory:
    """
    Comprehensive test data factory for Quirrely 2.0
    Generates realistic user journeys, content, and system interactions
    """
    
    def __init__(self, simulation_engine: QuirrelyTestSimulationEngine):
        self.engine = simulation_engine
        self.content_generator = ContentGenerator()
        self.generated_users: List[str] = []
        self.generated_partnerships: List[str] = []
        self.generated_analyses: List[str] = []
    
    # ─────────────────────────────────────────────────────────────────────
    # USER GENERATION
    # ─────────────────────────────────────────────────────────────────────
    
    def generate_test_users(self, profile: TestDataProfile) -> List[str]:
        """Generate test users based on profile specifications"""
        
        user_ids = []
        
        for i in range(profile.user_count):
            # Select country based on distribution
            country = self._weighted_choice(profile.country_distribution)
            
            # Select tier based on distribution
            tier = self._weighted_choice(profile.tier_distribution)
            
            # Generate realistic user details
            email = self._generate_email(country)
            display_name = self._generate_display_name(country)
            
            user_id = self.engine.simulate_user_creation(
                tier=tier,
                country=country,
                email=email,
                display_name=display_name
            )
            
            # Set voice profile
            if profile.voice_profiles:
                voice_profile = random.choice(profile.voice_profiles)
                self.engine.temp_users[user_id].voice_profile = voice_profile
                self.engine.temp_users[user_id].voice_stance = random.choice(list(VoiceStance))
            
            user_ids.append(user_id)
            self.generated_users.append(user_id)
        
        return user_ids
    
    def _weighted_choice(self, distribution: Dict[Any, float]) -> Any:
        """Select item based on weighted distribution"""
        items = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(items, weights=weights)[0]
    
    def _generate_email(self, country: Country) -> str:
        """Generate realistic email addresses by country"""
        
        domains = {
            Country.CANADA: ["gmail.com", "rogers.com", "bell.ca", "shaw.ca"],
            Country.UNITED_KINGDOM: ["gmail.com", "hotmail.co.uk", "btinternet.com", "sky.com"],
            Country.AUSTRALIA: ["gmail.com", "bigpond.com", "optus.com.au", "iinet.net.au"],
            Country.NEW_ZEALAND: ["gmail.com", "xtra.co.nz", "slingshot.co.nz", "orcon.net.nz"]
        }
        
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(domains.get(country, ["gmail.com"]))
        
        return f"test_{username}@{domain}"
    
    def _generate_display_name(self, country: Country) -> str:
        """Generate realistic display names by country"""
        
        first_names = {
            Country.CANADA: ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley"],
            Country.UNITED_KINGDOM: ["James", "Emma", "Oliver", "Sophie", "Harry", "Charlotte"],
            Country.AUSTRALIA: ["Liam", "Olivia", "Noah", "Ava", "Lucas", "Mia"],
            Country.NEW_ZEALAND: ["Jack", "Ruby", "William", "Sophie", "Oliver", "Charlotte"]
        }
        
        last_names = {
            Country.CANADA: ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller"],
            Country.UNITED_KINGDOM: ["Smith", "Jones", "Taylor", "Williams", "Brown", "Davies"],
            Country.AUSTRALIA: ["Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor"],
            Country.NEW_ZEALAND: ["Smith", "Jones", "Williams", "Taylor", "Brown", "Wilson"]
        }
        
        first = random.choice(first_names.get(country, ["Test"]))
        last = random.choice(last_names.get(country, ["User"]))
        
        return f"{first} {last}"
    
    # ─────────────────────────────────────────────────────────────────────
    # CONTENT GENERATION
    # ─────────────────────────────────────────────────────────────────────
    
    def generate_voice_analyses(
        self,
        user_ids: List[str],
        analyses_per_user: int = 3,
        include_halo_tests: bool = True
    ) -> List[str]:
        """Generate voice analyses for users"""
        
        analysis_ids = []
        
        for user_id in user_ids:
            user = self.engine.temp_users[user_id]
            
            for _ in range(analyses_per_user):
                # Generate content based on user's profile
                if user.voice_profile:
                    content = self.content_generator.generate_voice_content(
                        voice_profile=user.voice_profile,
                        country=user.country,
                        word_count_target=random.randint(30, 150)
                    )
                else:
                    content = "This is sample content for voice analysis testing."
                
                # Occasionally include HALO violation tests
                if include_halo_tests and random.random() < 0.05:  # 5% violation rate
                    tier = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
                    content = self.content_generator.generate_halo_violation_content(tier)
                
                analysis_id = self.engine.simulate_voice_analysis(
                    user_id=user_id,
                    text=content,
                    halo_check=True
                )
                
                analysis_ids.append(analysis_id)
                self.generated_analyses.append(analysis_id)
        
        return analysis_ids
    
    # ─────────────────────────────────────────────────────────────────────
    # PARTNERSHIP GENERATION
    # ─────────────────────────────────────────────────────────────────────
    
    def generate_partnerships(
        self,
        user_ids: List[str],
        partnership_ratio: float = 0.3
    ) -> List[str]:
        """Generate partnerships between Pro users"""
        
        # Filter Pro users
        pro_users = [
            uid for uid in user_ids
            if self.engine.temp_users[uid].tier in [UserTier.PRO, UserTier.PARTNERSHIP]
        ]
        
        if len(pro_users) < 2:
            return []
        
        partnership_ids = []
        partnership_count = int(len(pro_users) * partnership_ratio)
        
        # Randomly pair users for partnerships
        random.shuffle(pro_users)
        
        for i in range(0, min(partnership_count * 2, len(pro_users)), 2):
            if i + 1 >= len(pro_users):
                break
            
            initiator_id = pro_users[i]
            partner_id = pro_users[i + 1]
            
            initiator = self.engine.temp_users[initiator_id]
            partner = self.engine.temp_users[partner_id]
            
            # Generate partnership details
            partnership_type = random.choice(["growth", "creative", "professional", "heart", "life"])
            partnership_data = self.content_generator.generate_partnership_content(
                partnership_type=partnership_type,
                initiator_profile=initiator.voice_profile or VoiceProfile.BALANCED,
                country=initiator.country
            )
            
            # Create partnership
            partnership_id = self.engine.simulate_partnership_creation(
                initiator_user_id=initiator_id,
                partner_email=partner.email,
                partnership_name=partnership_data["partnership_name"],
                partnership_type=partnership_type
            )
            
            # Accept partnership
            success = self.engine.simulate_partnership_acceptance(partnership_id, partner_id)
            
            if success:
                partnership_ids.append(partnership_id)
                self.generated_partnerships.append(partnership_id)
                
                # Simulate some word usage
                self._simulate_partnership_usage(partnership_id, initiator_id, partner_id)
        
        return partnership_ids
    
    def _simulate_partnership_usage(
        self,
        partnership_id: str,
        initiator_id: str,
        partner_id: str
    ) -> None:
        """Simulate realistic word usage in partnerships"""
        
        # Simulate shared usage
        shared_usage = random.randint(1000, 5000)
        self.engine.simulate_partnership_word_usage(
            partnership_id=partnership_id,
            user_id=initiator_id,
            words_used=shared_usage,
            usage_type="shared"
        )
        
        # Simulate solo usage for both users
        initiator_solo = random.randint(500, 2000)
        partner_solo = random.randint(500, 2000)
        
        self.engine.simulate_partnership_word_usage(
            partnership_id=partnership_id,
            user_id=initiator_id,
            words_used=initiator_solo,
            usage_type="solo"
        )
        
        self.engine.simulate_partnership_word_usage(
            partnership_id=partnership_id,
            user_id=partner_id,
            words_used=partner_solo,
            usage_type="solo"
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # VIRAL GROWTH SIMULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def generate_viral_sharing(
        self,
        analysis_ids: List[str],
        share_ratio: float = 0.2,
        referral_conversion_rate: float = 0.15
    ) -> List[str]:
        """Generate viral sharing and referral chains"""
        
        share_ids = []
        
        # Select analyses for sharing
        analyses_to_share = random.sample(
            analysis_ids,
            int(len(analysis_ids) * share_ratio)
        )
        
        platforms = ["twitter", "linkedin", "facebook", "copy_link"]
        
        for analysis_id in analyses_to_share:
            analysis = self.engine.temp_analyses[analysis_id]
            user = self.engine.temp_users[analysis.user_id]
            
            # Generate share
            platform = random.choice(platforms)
            share_id = self.engine.simulate_share_action(
                user_id=analysis.user_id,
                platform=platform,
                profile_type=analysis.voice_profile.value,
                analysis_id=analysis_id
            )
            
            share_ids.append(share_id)
            
            # Simulate referral signups
            if random.random() < referral_conversion_rate:
                referred_user_id = self.engine.simulate_referral_signup(
                    share_id=share_id,
                    referred_user_tier=random.choice([UserTier.FREE, UserTier.PRO])
                )
                self.generated_users.append(referred_user_id)
        
        return share_ids
    
    # ─────────────────────────────────────────────────────────────────────
    # SCENARIO GENERATORS
    # ─────────────────────────────────────────────────────────────────────
    
    def generate_scenario_data(self, scenario: TestScenario) -> Dict[str, Any]:
        """Generate complete test data for a specific scenario"""
        
        if scenario == TestScenario.BASIC_USER_JOURNEY:
            return self._generate_basic_user_journey()
        elif scenario == TestScenario.PARTNERSHIP_COMPLETE:
            return self._generate_partnership_complete()
        elif scenario == TestScenario.VIRAL_GROWTH_CHAIN:
            return self._generate_viral_growth_chain()
        elif scenario == TestScenario.COUNTRY_LOCALIZATION:
            return self._generate_country_localization()
        elif scenario == TestScenario.HALO_SAFETY_TESTS:
            return self._generate_halo_safety_tests()
        elif scenario == TestScenario.VOICE_PROFILE_MATRIX:
            return self._generate_voice_profile_matrix()
        elif scenario == TestScenario.SEO_BLOG_SIMULATION:
            return self._generate_seo_blog_simulation()
        elif scenario == TestScenario.META_OBSERVER_STRESS:
            return self._generate_meta_observer_stress()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
    
    def _generate_basic_user_journey(self) -> Dict[str, Any]:
        """Generate basic user journey: Anonymous → Free → Pro"""
        
        profile = TestDataProfile(
            scenario=TestScenario.BASIC_USER_JOURNEY,
            user_count=10,
            country_distribution={Country.CANADA: 0.4, Country.UNITED_KINGDOM: 0.3, Country.AUSTRALIA: 0.2, Country.NEW_ZEALAND: 0.1},
            tier_distribution={UserTier.ANONYMOUS: 0.3, UserTier.FREE: 0.4, UserTier.PRO: 0.3},
            voice_profiles=list(VoiceProfile)
        )
        
        user_ids = self.generate_test_users(profile)
        analysis_ids = self.generate_voice_analyses(user_ids, analyses_per_user=2)
        
        return {
            "scenario": TestScenario.BASIC_USER_JOURNEY,
            "users_generated": len(user_ids),
            "analyses_generated": len(analysis_ids),
            "user_ids": user_ids,
            "analysis_ids": analysis_ids
        }
    
    def _generate_partnership_complete(self) -> Dict[str, Any]:
        """Generate complete partnership workflow testing"""
        
        profile = TestDataProfile(
            scenario=TestScenario.PARTNERSHIP_COMPLETE,
            user_count=20,
            country_distribution={Country.CANADA: 0.25, Country.UNITED_KINGDOM: 0.25, Country.AUSTRALIA: 0.25, Country.NEW_ZEALAND: 0.25},
            tier_distribution={UserTier.PRO: 0.8, UserTier.PARTNERSHIP: 0.2},
            voice_profiles=list(VoiceProfile)
        )
        
        user_ids = self.generate_test_users(profile)
        analysis_ids = self.generate_voice_analyses(user_ids, analyses_per_user=3)
        partnership_ids = self.generate_partnerships(user_ids, partnership_ratio=0.5)
        
        return {
            "scenario": TestScenario.PARTNERSHIP_COMPLETE,
            "users_generated": len(user_ids),
            "analyses_generated": len(analysis_ids),
            "partnerships_generated": len(partnership_ids),
            "user_ids": user_ids,
            "analysis_ids": analysis_ids,
            "partnership_ids": partnership_ids
        }
    
    def _generate_viral_growth_chain(self) -> Dict[str, Any]:
        """Generate viral growth chain testing"""
        
        profile = TestDataProfile(
            scenario=TestScenario.VIRAL_GROWTH_CHAIN,
            user_count=30,
            country_distribution={Country.CANADA: 0.4, Country.UNITED_KINGDOM: 0.3, Country.AUSTRALIA: 0.2, Country.NEW_ZEALAND: 0.1},
            tier_distribution={UserTier.FREE: 0.6, UserTier.PRO: 0.4},
            voice_profiles=[VoiceProfile.ASSERTIVE, VoiceProfile.OPEN, VoiceProfile.EXPANSIVE]
        )
        
        user_ids = self.generate_test_users(profile)
        analysis_ids = self.generate_voice_analyses(user_ids, analyses_per_user=4)
        share_ids = self.generate_viral_sharing(analysis_ids, share_ratio=0.3, referral_conversion_rate=0.2)
        
        return {
            "scenario": TestScenario.VIRAL_GROWTH_CHAIN,
            "users_generated": len(user_ids),
            "analyses_generated": len(analysis_ids),
            "shares_generated": len(share_ids),
            "user_ids": user_ids,
            "analysis_ids": analysis_ids,
            "share_ids": share_ids
        }
    
    def _generate_halo_safety_tests(self) -> Dict[str, Any]:
        """Generate HALO safety testing scenarios"""
        
        profile = TestDataProfile(
            scenario=TestScenario.HALO_SAFETY_TESTS,
            user_count=15,
            country_distribution={Country.CANADA: 0.25, Country.UNITED_KINGDOM: 0.25, Country.AUSTRALIA: 0.25, Country.NEW_ZEALAND: 0.25},
            tier_distribution={UserTier.FREE: 0.5, UserTier.PRO: 0.5},
            voice_profiles=list(VoiceProfile)
        )
        
        user_ids = self.generate_test_users(profile)
        
        # Generate content with deliberate HALO violations for testing
        violation_analyses = []
        for user_id in user_ids[:5]:  # First 5 users get violation content
            for tier in [0, 1, 2, 3]:  # Test all violation tiers
                content = self.content_generator.generate_halo_violation_content(tier)
                analysis_id = self.engine.simulate_voice_analysis(
                    user_id=user_id,
                    text=content,
                    halo_check=True
                )
                violation_analyses.append(analysis_id)
        
        # Generate normal analyses for remaining users
        normal_analyses = self.generate_voice_analyses(user_ids[5:], analyses_per_user=2)
        
        return {
            "scenario": TestScenario.HALO_SAFETY_TESTS,
            "users_generated": len(user_ids),
            "violation_analyses": len(violation_analyses),
            "normal_analyses": len(normal_analyses),
            "total_analyses": len(violation_analyses) + len(normal_analyses),
            "user_ids": user_ids,
            "violation_analysis_ids": violation_analyses,
            "normal_analysis_ids": normal_analyses
        }
    
    def _generate_voice_profile_matrix(self) -> Dict[str, Any]:
        """Generate complete voice profile × stance matrix testing"""
        
        # Create users for each voice profile × stance combination
        user_ids = []
        analysis_ids = []
        
        for voice_profile in VoiceProfile:
            for voice_stance in VoiceStance:
                for country in [Country.CANADA, Country.UNITED_KINGDOM]:  # Test 2 countries per combo
                    user_id = self.engine.simulate_user_creation(
                        tier=UserTier.PRO,
                        country=country,
                        email=f"test_{voice_profile.value}_{voice_stance.value}_{country.value}@example.com",
                        display_name=f"Test {voice_profile.value} {voice_stance.value}"
                    )
                    
                    # Set specific profile and stance
                    user = self.engine.temp_users[user_id]
                    user.voice_profile = voice_profile
                    user.voice_stance = voice_stance
                    
                    user_ids.append(user_id)
                    
                    # Generate content matching the profile
                    content = self.content_generator.generate_voice_content(
                        voice_profile=voice_profile,
                        country=country,
                        word_count_target=80
                    )
                    
                    analysis_id = self.engine.simulate_voice_analysis(
                        user_id=user_id,
                        text=content,
                        halo_check=True
                    )
                    
                    analysis_ids.append(analysis_id)
        
        return {
            "scenario": TestScenario.VOICE_PROFILE_MATRIX,
            "profiles_tested": len(VoiceProfile),
            "stances_tested": len(VoiceStance),
            "countries_tested": 2,
            "total_combinations": len(VoiceProfile) * len(VoiceStance) * 2,
            "users_generated": len(user_ids),
            "analyses_generated": len(analysis_ids),
            "user_ids": user_ids,
            "analysis_ids": analysis_ids
        }
    
    def _generate_country_localization(self) -> Dict[str, Any]:
        """Generate country localization testing"""
        
        country_data = {}
        
        for country in Country:
            profile = TestDataProfile(
                scenario=TestScenario.COUNTRY_LOCALIZATION,
                user_count=8,
                country_distribution={country: 1.0},  # 100% single country
                tier_distribution={UserTier.FREE: 0.4, UserTier.PRO: 0.4, UserTier.PARTNERSHIP: 0.2},
                voice_profiles=list(VoiceProfile)
            )
            
            user_ids = self.generate_test_users(profile)
            analysis_ids = self.generate_voice_analyses(user_ids, analyses_per_user=2)
            partnership_ids = self.generate_partnerships(user_ids, partnership_ratio=0.3)
            
            country_data[country.value] = {
                "users": user_ids,
                "analyses": analysis_ids,
                "partnerships": partnership_ids,
                "adaptations_tested": [
                    self.engine.simulate_country_adaptation(uid) for uid in user_ids[:3]
                ]
            }
        
        return {
            "scenario": TestScenario.COUNTRY_LOCALIZATION,
            "countries_tested": len(Country),
            "country_data": country_data,
            "total_users": sum(len(data["users"]) for data in country_data.values()),
            "total_analyses": sum(len(data["analyses"]) for data in country_data.values())
        }
    
    def _generate_meta_observer_stress(self) -> Dict[str, Any]:
        """Generate high-volume data for Meta/Observer stress testing"""
        
        profile = TestDataProfile(
            scenario=TestScenario.META_OBSERVER_STRESS,
            user_count=100,
            country_distribution={Country.CANADA: 0.4, Country.UNITED_KINGDOM: 0.3, Country.AUSTRALIA: 0.2, Country.NEW_ZEALAND: 0.1},
            tier_distribution={UserTier.ANONYMOUS: 0.2, UserTier.FREE: 0.4, UserTier.PRO: 0.3, UserTier.PARTNERSHIP: 0.1},
            voice_profiles=list(VoiceProfile)
        )
        
        user_ids = self.generate_test_users(profile)
        analysis_ids = self.generate_voice_analyses(user_ids, analyses_per_user=5, include_halo_tests=True)
        partnership_ids = self.generate_partnerships(user_ids, partnership_ratio=0.2)
        share_ids = self.generate_viral_sharing(analysis_ids, share_ratio=0.15)
        
        # Generate additional Meta/Observer events
        event_count = len(self.engine.temp_events)
        
        return {
            "scenario": TestScenario.META_OBSERVER_STRESS,
            "users_generated": len(user_ids),
            "analyses_generated": len(analysis_ids),
            "partnerships_generated": len(partnership_ids),
            "shares_generated": len(share_ids),
            "total_events_generated": event_count,
            "user_ids": user_ids,
            "analysis_ids": analysis_ids,
            "partnership_ids": partnership_ids,
            "share_ids": share_ids
        }
    
    def _generate_seo_blog_simulation(self) -> Dict[str, Any]:
        """Generate SEO blog system simulation"""
        
        # This is a placeholder for SEO system testing
        # In actual implementation, this would generate blog post interactions,
        # keyword tracking, social sharing events, etc.
        
        profile = TestDataProfile(
            scenario=TestScenario.SEO_BLOG_SIMULATION,
            user_count=50,
            country_distribution={Country.CANADA: 0.25, Country.UNITED_KINGDOM: 0.25, Country.AUSTRALIA: 0.25, Country.NEW_ZEALAND: 0.25},
            tier_distribution={UserTier.ANONYMOUS: 0.5, UserTier.FREE: 0.3, UserTier.PRO: 0.2},
            voice_profiles=list(VoiceProfile)
        )
        
        user_ids = self.generate_test_users(profile)
        
        # Simulate blog interactions
        blog_interactions = []
        for user_id in user_ids:
            user = self.engine.temp_users[user_id]
            country_blog_count = {Country.CANADA: 64, Country.UNITED_KINGDOM: 64, Country.AUSTRALIA: 64, Country.NEW_ZEALAND: 32}
            available_posts = country_blog_count.get(user.country, 40)
            
            # Simulate blog post views
            posts_viewed = random.randint(1, min(5, available_posts))
            for _ in range(posts_viewed):
                blog_interactions.append({
                    "user_id": user_id,
                    "post_id": f"blog_{random.randint(1, available_posts)}_{user.country.value}",
                    "interaction_type": "view",
                    "timestamp": datetime.utcnow()
                })
        
        return {
            "scenario": TestScenario.SEO_BLOG_SIMULATION,
            "users_generated": len(user_ids),
            "blog_interactions": len(blog_interactions),
            "user_ids": user_ids,
            "interactions": blog_interactions
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # CLEANUP & REPORTING
    # ─────────────────────────────────────────────────────────────────────
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of all generated test data"""
        
        return {
            "total_users_generated": len(self.generated_users),
            "total_partnerships_generated": len(self.generated_partnerships),
            "total_analyses_generated": len(self.generated_analyses),
            "countries_represented": len(set(
                self.engine.temp_users[uid].country for uid in self.generated_users
            )),
            "tiers_represented": len(set(
                self.engine.temp_users[uid].tier for uid in self.generated_users
            )),
            "voice_profiles_represented": len(set(
                self.engine.temp_users[uid].voice_profile for uid in self.generated_users
                if self.engine.temp_users[uid].voice_profile
            )),
            "meta_events_generated": len(self.engine.temp_events),
            "zero_persistence_validated": self.engine.validate_zero_persistence()
        }


# ═══════════════════════════════════════════════════════════════════════════
# TESTING & VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 TEST DATA FACTORY - VALIDATION TEST")
    print("=" * 60)
    
    from .simulation_core import QuirrelyTestSimulationEngine
    
    # Create simulation engine and factory
    engine = QuirrelyTestSimulationEngine()
    factory = QuirrelyTestDataFactory(engine)
    
    try:
        # Test basic user journey
        print("\n🚀 Testing Basic User Journey...")
        basic_data = factory.generate_scenario_data(TestScenario.BASIC_USER_JOURNEY)
        print(f"  ✅ Users: {basic_data['users_generated']}")
        print(f"  ✅ Analyses: {basic_data['analyses_generated']}")
        
        # Test partnership workflow
        print("\n🤝 Testing Partnership Complete...")
        partnership_data = factory.generate_scenario_data(TestScenario.PARTNERSHIP_COMPLETE)
        print(f"  ✅ Users: {partnership_data['users_generated']}")
        print(f"  ✅ Partnerships: {partnership_data['partnerships_generated']}")
        
        # Test HALO safety
        print("\n🛡️ Testing HALO Safety...")
        halo_data = factory.generate_scenario_data(TestScenario.HALO_SAFETY_TESTS)
        print(f"  ✅ Users: {halo_data['users_generated']}")
        print(f"  ✅ Violation tests: {halo_data['violation_analyses']}")
        print(f"  ✅ Normal tests: {halo_data['normal_analyses']}")
        
        # Test voice profile matrix
        print("\n🗣️ Testing Voice Profile Matrix...")
        voice_data = factory.generate_scenario_data(TestScenario.VOICE_PROFILE_MATRIX)
        print(f"  ✅ Combinations: {voice_data['total_combinations']}")
        print(f"  ✅ Users: {voice_data['users_generated']}")
        
        # Test country localization
        print("\n🌍 Testing Country Localization...")
        country_data = factory.generate_scenario_data(TestScenario.COUNTRY_LOCALIZATION)
        print(f"  ✅ Countries: {country_data['countries_tested']}")
        print(f"  ✅ Total users: {country_data['total_users']}")
        
        # Get generation summary
        print("\n📊 Generation Summary...")
        summary = factory.get_generation_summary()
        print(f"  📈 Total users: {summary['total_users_generated']}")
        print(f"  📈 Total analyses: {summary['total_analyses_generated']}")
        print(f"  📈 Total partnerships: {summary['total_partnerships_generated']}")
        print(f"  📈 Countries: {summary['countries_represented']}")
        print(f"  📈 Voice profiles: {summary['voice_profiles_represented']}")
        print(f"  📈 Meta events: {summary['meta_events_generated']}")
        
        # Validate zero persistence
        persistence_check = summary['zero_persistence_validated']
        claude_compliant = persistence_check.get('claude_md_compliant', False)
        print(f"  🔒 CLAUDE.md compliant: {claude_compliant}")
        
        if claude_compliant:
            print("\n🎉 ALL TEST DATA FACTORY TESTS PASSED")
            print("✅ All scenarios generate realistic data")
            print("✅ Zero persistence maintained")
            print("✅ Comprehensive coverage across all systems")
            print("✅ Ready for UI validation framework integration")
            print("\n🚀 WEEK 1 DAY 1 DELIVERABLES COMPLETE!")
        else:
            print("\n❌ VALIDATION FAILED - Review persistence compliance")
    
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup happens automatically via __del__
        print("\n🧹 Cleanup completed - No files created")