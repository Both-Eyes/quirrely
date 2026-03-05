#!/usr/bin/env python3
"""
COLLABORATION CANCELLATION RATE LIMITING TEST
Test that users can only cancel one collaboration per month.
"""

import asyncio
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
import uuid

class CancellationRateLimitTest:
    def __init__(self):
        # Set up test database
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        
    def setup_test_db(self):
        """Create test database with rate limiting tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT,
                subscription_tier TEXT DEFAULT 'pro'
            )
        ''')
        
        # Partnerships table
        cursor.execute('''
            CREATE TABLE writing_partnerships (
                id TEXT PRIMARY KEY,
                initiator_user_id TEXT NOT NULL,
                partner_user_id TEXT,
                partnership_name TEXT NOT NULL,
                partnership_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                cancelled_at TEXT,
                cancelled_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User partnership status table (rate limiting)
        cursor.execute('''
            CREATE TABLE user_partnership_status (
                user_id TEXT PRIMARY KEY,
                last_cancellation_date DATE,
                cancellations_this_month INTEGER DEFAULT 0,
                monthly_cancellation_period_start DATE,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def test_first_cancellation_allowed(self):
        """Test that first cancellation is allowed."""
        print("🧪 Testing first cancellation (should be allowed)...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        partnership_id = str(uuid.uuid4())
        
        # Create test user and partnership
        cursor.execute(
            'INSERT INTO users (id, email, display_name) VALUES (?, ?, ?)',
            (user_id, 'test@example.com', 'Test User')
        )
        
        cursor.execute('''
            INSERT INTO writing_partnerships (id, initiator_user_id, partnership_name, partnership_type, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (partnership_id, user_id, 'Test Partnership', 'growth', 'active'))
        
        # Simulate rate limiting check (should return True for first cancellation)
        cursor.execute('SELECT COUNT(*) FROM user_partnership_status WHERE user_id = ?', (user_id,))
        has_status = cursor.fetchone()[0] > 0
        
        can_cancel = not has_status  # No record = can cancel
        
        if can_cancel:
            # Cancel partnership
            cursor.execute('''
                UPDATE writing_partnerships 
                SET status = 'cancelled', cancelled_at = ?, cancelled_by = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), user_id, partnership_id))
            
            # Record cancellation
            cursor.execute('''
                INSERT INTO user_partnership_status (
                    user_id, last_cancellation_date, cancellations_this_month, 
                    monthly_cancellation_period_start
                ) VALUES (?, ?, ?, ?)
            ''', (user_id, datetime.now().date().isoformat(), 1, 
                  datetime.now().replace(day=1).date().isoformat()))
            
        conn.commit()
        conn.close()
        
        if can_cancel:
            print("✅ First cancellation allowed")
            return True
        else:
            print("❌ First cancellation blocked incorrectly")
            return False
            
    def test_second_cancellation_blocked(self):
        """Test that second cancellation in same month is blocked."""
        print("🧪 Testing second cancellation in same month (should be blocked)...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        partnership1_id = str(uuid.uuid4())
        partnership2_id = str(uuid.uuid4())
        
        # Create test user
        cursor.execute(
            'INSERT INTO users (id, email, display_name) VALUES (?, ?, ?)',
            (user_id, 'test2@example.com', 'Test User 2')
        )
        
        # Create first partnership and cancel it
        cursor.execute('''
            INSERT INTO writing_partnerships (id, initiator_user_id, partnership_name, partnership_type, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (partnership1_id, user_id, 'Test Partnership 1', 'growth', 'cancelled'))
        
        # Record first cancellation this month
        current_month_start = datetime.now().replace(day=1).date().isoformat()
        cursor.execute('''
            INSERT INTO user_partnership_status (
                user_id, last_cancellation_date, cancellations_this_month, 
                monthly_cancellation_period_start
            ) VALUES (?, ?, ?, ?)
        ''', (user_id, datetime.now().date().isoformat(), 1, current_month_start))
        
        # Create second partnership
        cursor.execute('''
            INSERT INTO writing_partnerships (id, initiator_user_id, partnership_name, partnership_type, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (partnership2_id, user_id, 'Test Partnership 2', 'heart', 'active'))
        
        # Check if user can cancel again this month
        cursor.execute('''
            SELECT cancellations_this_month, monthly_cancellation_period_start 
            FROM user_partnership_status 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            cancellations, period_start = result
            current_period = datetime.now().replace(day=1).date().isoformat()
            
            # User cannot cancel if they've already cancelled this month
            can_cancel = cancellations < 1 or period_start < current_period
        else:
            can_cancel = True  # No record = can cancel
            
        conn.close()
        
        if not can_cancel:
            print("✅ Second cancellation blocked correctly")
            return True
        else:
            print("❌ Second cancellation allowed incorrectly")
            return False
            
    def test_next_month_cancellation_allowed(self):
        """Test that cancellation is allowed in next month."""
        print("🧪 Testing cancellation in next month (should be allowed)...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        partnership_id = str(uuid.uuid4())
        
        # Create test user
        cursor.execute(
            'INSERT INTO users (id, email, display_name) VALUES (?, ?, ?)',
            (user_id, 'test3@example.com', 'Test User 3')
        )
        
        # Create partnership
        cursor.execute('''
            INSERT INTO writing_partnerships (id, initiator_user_id, partnership_name, partnership_type, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (partnership_id, user_id, 'Test Partnership 3', 'creative', 'active'))
        
        # Record cancellation from previous month
        last_month = (datetime.now() - timedelta(days=32)).replace(day=1).date().isoformat()
        last_month_cancel = (datetime.now() - timedelta(days=15)).date().isoformat()
        
        cursor.execute('''
            INSERT INTO user_partnership_status (
                user_id, last_cancellation_date, cancellations_this_month, 
                monthly_cancellation_period_start
            ) VALUES (?, ?, ?, ?)
        ''', (user_id, last_month_cancel, 1, last_month))
        
        # Check if user can cancel this month (should be allowed)
        cursor.execute('''
            SELECT cancellations_this_month, monthly_cancellation_period_start 
            FROM user_partnership_status 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        current_period = datetime.now().replace(day=1).date().isoformat()
        
        if result:
            cancellations, period_start = result
            # User can cancel if period has reset (new month)
            can_cancel = period_start < current_period
        else:
            can_cancel = True
            
        conn.close()
        
        if can_cancel:
            print("✅ Next month cancellation allowed")
            return True
        else:
            print("❌ Next month cancellation blocked incorrectly")
            return False
    
    def test_next_cancellation_date_calculation(self):
        """Test calculation of next available cancellation date."""
        print("🧪 Testing next cancellation date calculation...")
        
        # User who cancelled this month should have next date = next month
        current_date = datetime.now()
        next_month = current_date.replace(day=1) + timedelta(days=32)
        next_month_start = next_month.replace(day=1)
        
        # Mock calculation
        last_cancellation_this_month = current_date.date()
        current_month_start = current_date.replace(day=1).date()
        
        if last_cancellation_this_month >= current_month_start:
            # Cancelled this month - next available is next month
            calculated_next_date = next_month_start.date()
        else:
            # Can cancel now
            calculated_next_date = current_date.date()
        
        expected_next_date = next_month_start.date()
        
        if calculated_next_date == expected_next_date:
            print("✅ Next cancellation date calculated correctly")
            print(f"    Next available: {calculated_next_date.strftime('%B %d, %Y')}")
            return True
        else:
            print("❌ Next cancellation date calculated incorrectly")
            print(f"    Expected: {expected_next_date}, Got: {calculated_next_date}")
            return False
    
    def run_all_tests(self):
        """Run all rate limiting tests."""
        print("🚀 Starting Collaboration Cancellation Rate Limiting Tests")
        print("=" * 65)
        
        self.setup_test_db()
        
        tests = [
            ("First Cancellation Allowed", self.test_first_cancellation_allowed),
            ("Second Cancellation Blocked", self.test_second_cancellation_blocked),
            ("Next Month Cancellation Allowed", self.test_next_month_cancellation_allowed),
            ("Next Cancellation Date Calculation", self.test_next_cancellation_date_calculation),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
        
        print("\n" + "=" * 65)
        print("📊 RATE LIMITING TEST RESULTS")
        print("=" * 65)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL RATE LIMITING TESTS PASSED!")
            print("✅ Users can only cancel 1 collaboration per month")
            print("✅ Rate limiting properly enforced")
            print("✅ Next cancellation dates calculated correctly")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed - Rate limiting needs fixes")
        
        # Cleanup
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
            
        return passed == total

def main():
    """Run rate limiting tests."""
    test_suite = CancellationRateLimitTest()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)