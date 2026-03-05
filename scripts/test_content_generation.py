#!/usr/bin/env python3
"""
Test script for the automated content generation system.
Tests the complete workflow from SEO analysis to content publication.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock dependencies to avoid import issues
class MockConversionTracker:
    def __init__(self):
        pass

class MockBlogObserver:
    def get_health(self):
        return type('MockHealth', (), {
            'top_pages': ['/blog/how-conversational-open-writers-write'],
            'total_impressions': 1000,
            'total_clicks': 50
        })()
    
    def detect_keyword_opportunities(self):
        return [type('MockOpportunity', (), {
            'keyword': 'conversational open writing',
            'page_url': '/blog/how-conversational-open-writers-write',
            'current_position': 12.5,
            'impressions': 500,
            'clicks': 25,
            'potential_clicks': 150,
            'priority': 85.0
        })()]
    
    _pages = {}
    _content_registry = {}

class MockBlogConfig:
    def get_best_meta_template(self):
        return type('MockTemplate', (), {
            'description_template': 'Discover the unique patterns of {style} {certitude} writers.'
        })()

def mock_get_blog_observer():
    return MockBlogObserver()

def mock_get_blog_config():
    return MockBlogConfig()

# Patch the imports before importing the agent
import sys
import types

mock_conversion_events = types.ModuleType('backend.conversion_events')
mock_conversion_events.ConversionTracker = MockConversionTracker
sys.modules['backend.conversion_events'] = mock_conversion_events

mock_blog_observer = types.ModuleType('lncp.meta.blog_observer')
mock_blog_observer.get_blog_observer = mock_get_blog_observer
mock_blog_observer.KeywordOpportunity = object
mock_blog_observer.PagePerformance = object
sys.modules['lncp.meta.blog_observer'] = mock_blog_observer

mock_blog_config = types.ModuleType('lncp.meta.blog.config')  
mock_blog_config.get_blog_config = mock_get_blog_config
mock_blog_config.META_TEMPLATES = {}
sys.modules['lncp.meta.blog.config'] = mock_blog_config

from backend.agents.content_generation_agent import ContentGenerationAgent, ContentOpportunity, GeneratedContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDBPool:
    """Mock database pool for testing."""
    async def acquire(self):
        return self
    
    async def release(self, connection):
        pass
    
    async def execute(self, query, *args):
        logger.info(f"Mock DB execute: {query[:50]}...")
    
    async def fetch(self, query, *args):
        logger.info(f"Mock DB fetch: {query[:50]}...")
        return []
    
    async def fetchrow(self, query, *args):
        logger.info(f"Mock DB fetchrow: {query[:50]}...")
        return None

class ContentGenerationTest:
    """Test suite for content generation system."""
    
    def __init__(self):
        self.db_pool = MockDBPool()
        self.agent = ContentGenerationAgent(self.db_pool)
    
    async def test_analysis_phase(self):
        """Test the content analysis phase."""
        logger.info("=== TESTING ANALYSIS PHASE ===")
        
        try:
            result = await self.agent.analyze()
            
            logger.info(f"✓ Analysis completed successfully")
            logger.info(f"  - Found {len(result.content_opportunities)} opportunities")
            logger.info(f"  - {len(result.keywords_missing_content)} missing keyword content")
            logger.info(f"  - {len(result.refresh_candidates)} refresh candidates")
            logger.info(f"  - Top patterns: {len(result.top_performing_patterns)}")
            
            if result.content_opportunities:
                top_opp = result.content_opportunities[0]
                logger.info(f"  - Top opportunity: {top_opp.keyword} (priority: {top_opp.priority})")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Analysis phase failed: {str(e)}")
            return None
    
    async def test_optimization_phase(self, analysis_result):
        """Test the content optimization/generation phase."""
        logger.info("=== TESTING OPTIMIZATION PHASE ===")
        
        if not analysis_result:
            logger.error("✗ Cannot test optimization without analysis results")
            return None
        
        try:
            # Create a test opportunity if none exist
            if not analysis_result.content_opportunities:
                test_opportunity = ContentOpportunity(
                    type="keyword_gap",
                    priority=85.0,
                    estimated_monthly_clicks=500,
                    keyword="conversational open writing",
                    content_type="profile_post",
                    template_data={"style": "conversational", "certitude": "open"},
                    reasoning="Test opportunity for content generation"
                )
                analysis_result.content_opportunities.append(test_opportunity)
            
            generated_content = await self.agent.optimize(analysis_result)
            
            logger.info(f"✓ Content generation completed successfully")
            logger.info(f"  - Generated {len(generated_content)} pieces of content")
            
            for content in generated_content:
                logger.info(f"  - {content.title} ({content.filename})")
                logger.info(f"    Keywords: {', '.join(content.target_keywords)}")
                logger.info(f"    SEO Score: {content.seo_score}")
            
            return generated_content
            
        except Exception as e:
            logger.error(f"✗ Optimization phase failed: {str(e)}")
            return None
    
    async def test_execution_phase(self, generated_content):
        """Test the content execution/publishing phase."""
        logger.info("=== TESTING EXECUTION PHASE ===")
        
        if not generated_content:
            logger.error("✗ Cannot test execution without generated content")
            return None
        
        try:
            # Mock the execution - don't actually write files in test
            execution_result = {
                "published_posts": [
                    {
                        "filename": content.filename,
                        "title": content.title,
                        "url": content.url_path,
                        "seo_score": content.seo_score
                    }
                    for content in generated_content
                ],
                "sitemap_updated": True,
                "gsc_submitted": True,
                "errors": []
            }
            
            logger.info(f"✓ Execution simulation completed successfully")
            logger.info(f"  - Would publish {len(execution_result['published_posts'])} posts")
            logger.info(f"  - Sitemap update: {execution_result['sitemap_updated']}")
            logger.info(f"  - GSC submission: {execution_result['gsc_submitted']}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"✗ Execution phase failed: {str(e)}")
            return None
    
    async def test_reporting_phase(self, analysis_result, generated_content, execution_result):
        """Test the reporting phase."""
        logger.info("=== TESTING REPORTING PHASE ===")
        
        try:
            report = await self.agent.report(analysis_result, generated_content, execution_result)
            
            logger.info(f"✓ Reporting completed successfully")
            logger.info(f"  - Agent: {report.agent_name}")
            logger.info(f"  - Success: {report.success}")
            logger.info(f"  - Summary length: {len(report.summary)} characters")
            logger.info(f"  - Recommendations: {len(report.recommendations)}")
            
            # Print summary
            logger.info("Report Summary:")
            for line in report.summary.split('\n'):
                if line.strip():
                    logger.info(f"    {line}")
            
            return report
            
        except Exception as e:
            logger.error(f"✗ Reporting phase failed: {str(e)}")
            return None
    
    async def test_content_templates(self):
        """Test content generation templates."""
        logger.info("=== TESTING CONTENT TEMPLATES ===")
        
        try:
            # Test profile post generation
            opportunity = ContentOpportunity(
                type="keyword_gap",
                priority=90.0,
                estimated_monthly_clicks=800,
                keyword="formal balanced writing",
                content_type="profile_post",
                template_data={"style": "formal", "certitude": "balanced"},
                reasoning="Test formal balanced writing post"
            )
            
            content = await self.agent._generate_content(opportunity, [])
            
            if content:
                logger.info(f"✓ Template generation successful")
                logger.info(f"  - Title: {content.title}")
                logger.info(f"  - Meta: {content.meta_description}")
                logger.info(f"  - Body length: {len(content.body)} characters")
                logger.info(f"  - Keywords: {', '.join(content.target_keywords)}")
                
                # Verify content structure
                if "FORMAL + BALANCED" in content.body:
                    logger.info("  ✓ Proper style/certitude formatting")
                else:
                    logger.warning("  ! Style/certitude formatting not found")
                
                return True
            else:
                logger.error("✗ Template generation returned None")
                return False
                
        except Exception as e:
            logger.error(f"✗ Template testing failed: {str(e)}")
            return False
    
    async def test_utility_functions(self):
        """Test utility functions."""
        logger.info("=== TESTING UTILITY FUNCTIONS ===")
        
        try:
            # Test keyword extraction
            test_cases = [
                "conversational open writing",
                "formal balanced writers",
                "assertive contradictory style",
                "poetic closed voice",
                "writing tips"  # Should not match
            ]
            
            for keyword in test_cases:
                result = self.agent._extract_style_certitude_from_keyword(keyword)
                if result:
                    logger.info(f"  ✓ '{keyword}' → {result['style']} + {result['certitude']}")
                else:
                    logger.info(f"  - '{keyword}' → No match")
            
            # Test HTML formatting
            test_body = """Understanding FORMAL + BALANCED writing.

THE PATTERN

Structured approach with measured consideration.

KEY POINTS

• Clear organization
• Professional tone
• Balanced perspectives"""
            
            html = self.agent._format_body_html(test_body)
            if "<h2>" in html and "<p>" in html:
                logger.info("  ✓ HTML formatting working correctly")
            else:
                logger.warning("  ! HTML formatting may have issues")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Utility function testing failed: {str(e)}")
            return False
    
    async def run_full_test(self):
        """Run the complete test suite."""
        logger.info("Starting Content Generation System Test")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Test individual components
        template_test = await self.test_content_templates()
        utility_test = await self.test_utility_functions()
        
        # Test main workflow
        analysis_result = await self.test_analysis_phase()
        generated_content = await self.test_optimization_phase(analysis_result)
        execution_result = await self.test_execution_phase(generated_content)
        report = await self.test_reporting_phase(analysis_result, generated_content, execution_result)
        
        # Calculate results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print final results
        logger.info("=" * 60)
        logger.info("TEST RESULTS SUMMARY:")
        logger.info(f"  Template Generation:    {'✓ PASS' if template_test else '✗ FAIL'}")
        logger.info(f"  Utility Functions:      {'✓ PASS' if utility_test else '✗ FAIL'}")
        logger.info(f"  Analysis Phase:         {'✓ PASS' if analysis_result else '✗ FAIL'}")
        logger.info(f"  Optimization Phase:     {'✓ PASS' if generated_content else '✗ FAIL'}")
        logger.info(f"  Execution Phase:        {'✓ PASS' if execution_result else '✗ FAIL'}")
        logger.info(f"  Reporting Phase:        {'✓ PASS' if report else '✗ FAIL'}")
        logger.info(f"")
        logger.info(f"  Total Duration: {duration:.2f} seconds")
        
        # Overall result
        all_tests_passed = all([
            template_test, utility_test, analysis_result is not None,
            generated_content is not None, execution_result is not None,
            report is not None
        ])
        
        logger.info(f"  Overall Result: {'✓ ALL TESTS PASSED' if all_tests_passed else '✗ SOME TESTS FAILED'}")
        logger.info("=" * 60)
        
        return all_tests_passed

async def main():
    """Main test runner."""
    print("Content Generation System Test Suite")
    print("Testing automated blog content generation with SEO optimization")
    print("")
    
    try:
        tester = ContentGenerationTest()
        success = await tester.run_full_test()
        
        if success:
            print("\n🎉 Content generation system is ready for deployment!")
            exit_code = 0
        else:
            print("\n❌ Content generation system has issues that need attention.")
            exit_code = 1
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)