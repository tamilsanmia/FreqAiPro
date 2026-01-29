#!/usr/bin/env python3
"""
Test concurrent database access to verify locking issues are resolved
"""
import sqlite3
import threading
import time
import random
import logging

logging.basicConfig(
    filename='logs/test_concurrent.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_FILE = 'signals.db'
NUM_THREADS = 5
NUM_OPERATIONS = 10

def test_read_write():
    """Simulate concurrent read/write operations"""
    thread_id = threading.current_thread().name
    
    for i in range(NUM_OPERATIONS):
        try:
            # Test write operation
            conn = sqlite3.connect(DB_FILE, timeout=30)
            c = conn.cursor()
            c.execute("INSERT INTO signals (coin, signal_type, price, strength, st_level, timeframe) VALUES (?, ?, ?, ?, ?, ?)",
                      (f'TEST{i}', 'BUY', random.uniform(100, 200), 'NORMAL', random.uniform(90, 110), '5m'))
            conn.commit()
            conn.close()
            logger.info(f"{thread_id}: Write operation {i+1} successful")
            
            # Small delay between operations
            time.sleep(random.uniform(0.01, 0.1))
            
            # Test read operation
            conn = sqlite3.connect(DB_FILE, timeout=30)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM signals")
            count = c.fetchone()[0]
            conn.close()
            logger.info(f"{thread_id}: Read operation {i+1} successful (total signals: {count})")
            
        except sqlite3.OperationalError as e:
            logger.error(f"{thread_id}: Database error on operation {i+1}: {e}")
            return False
        except Exception as e:
            logger.error(f"{thread_id}: Unexpected error on operation {i+1}: {e}")
            return False
    
    logger.info(f"{thread_id}: Completed all {NUM_OPERATIONS} operations")
    return True

def test_position_operations():
    """Simulate position creation and updates"""
    thread_id = threading.current_thread().name
    
    for i in range(NUM_OPERATIONS):
        try:
            conn = sqlite3.connect(DB_FILE, timeout=30)
            c = conn.cursor()
            
            # Insert position
            coin = f'POS{i}'
            entry_price = random.uniform(100, 500)
            c.execute("INSERT INTO positions (coin, entry_price, sl, tp1, tp2, tp3, status, timeframe) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (coin, entry_price, entry_price * 0.98, entry_price * 1.01, entry_price * 1.02, entry_price * 1.03, 'open', '5m'))
            
            conn.commit()
            logger.info(f"{thread_id}: Position insert operation {i+1} successful")
            
            # Update position
            c.execute("UPDATE positions SET status='closed' WHERE coin=?", (coin,))
            conn.commit()
            conn.close()
            logger.info(f"{thread_id}: Position update operation {i+1} successful")
            
            time.sleep(random.uniform(0.01, 0.1))
            
        except sqlite3.OperationalError as e:
            logger.error(f"{thread_id}: Database error on operation {i+1}: {e}")
            return False
        except Exception as e:
            logger.error(f"{thread_id}: Unexpected error on operation {i+1}: {e}")
            return False
    
    logger.info(f"{thread_id}: Completed all position operations")
    return True

def run_concurrent_test():
    """Run concurrent database access test"""
    logger.info("=" * 60)
    logger.info(f"Starting concurrent database test with {NUM_THREADS} threads")
    logger.info(f"Each thread will perform {NUM_OPERATIONS} operations")
    logger.info("=" * 60)
    
    threads = []
    results = []
    
    # Create and start threads
    for i in range(NUM_THREADS):
        if i % 2 == 0:
            thread = threading.Thread(target=lambda r=results: r.append(test_read_write()), name=f"ReadWrite-{i+1}")
        else:
            thread = threading.Thread(target=lambda r=results: r.append(test_position_operations()), name=f"Position-{i+1}")
        
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    logger.info("=" * 60)
    logger.info(f"Test completed. Success rate: {sum(results)}/{len(results)}")
    logger.info("=" * 60)
    
    return all(results)

if __name__ == '__main__':
    print("\nRunning concurrent database access test...")
    print("Check logs/test_concurrent.log for detailed results")
    
    success = run_concurrent_test()
    
    if success:
        print("\n✓ All concurrent operations completed successfully!")
        print("Database locking issue appears to be resolved.")
    else:
        print("\n✗ Some operations failed. Check test_concurrent.log")
