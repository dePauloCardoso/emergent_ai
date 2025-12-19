#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Volo Web Scraping System
Tests all endpoints and web scraping functionality
"""

import requests
import sys
import json
import time
from datetime import datetime

class VoloWebScrapingTester:
    def __init__(self, base_url="https://travel-promo-radar-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Volo-Test-Client/1.0'
        })

    def log_test(self, name, success, details="", expected="", actual=""):
        """Log test results"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} - {name}")
        
        if details:
            print(f"   Details: {details}")
        if expected and actual:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
            
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append({
                "test": name,
                "details": details,
                "expected": expected,
                "actual": actual
            })

    def test_health_endpoint(self):
        """Test /api/health endpoint for web scraping status"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Health Endpoint", False, 
                            f"Status code {response.status_code}", "200", str(response.status_code))
                return False
                
            data = response.json()
            
            # Check scraping_method
            if data.get('scraping_method') != 'direct_web_scraping':
                self.log_test("Health - Scraping Method", False,
                            "Wrong scraping method", "direct_web_scraping", data.get('scraping_method'))
                return False
                
            self.log_test("Health Endpoint", True, "Web scraping method confirmed")
            return True
            
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_scraping_info_endpoint(self):
        """Test /api/scraping-info endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/scraping-info", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Scraping Info Endpoint", False,
                            f"Status code {response.status_code}", "200", str(response.status_code))
                return False
                
            data = response.json()
            
            # Check flight sources
            flight_sources = data.get('flight_sources', {})
            if flight_sources.get('total') != 10:
                self.log_test("Scraping Info - Flight Sources Count", False,
                            "Wrong number of airlines", "10", str(flight_sources.get('total')))
                return False
                
            # Check cruise sources  
            cruise_sources = data.get('cruise_sources', {})
            if cruise_sources.get('total') != 10:
                self.log_test("Scraping Info - Cruise Sources Count", False,
                            "Wrong number of cruise lines", "10", str(cruise_sources.get('total')))
                return False
                
            # Verify some expected airlines
            airlines = flight_sources.get('airlines', [])
            expected_airlines = ['United Airlines', 'American Airlines', 'Delta', 'Emirates']
            for airline in expected_airlines:
                if airline not in airlines:
                    self.log_test("Scraping Info - Airlines List", False,
                                f"Missing airline: {airline}")
                    return False
                    
            # Verify some expected cruise lines
            cruise_lines = cruise_sources.get('cruise_lines', [])
            expected_cruise_lines = ['Royal Caribbean', 'Carnival Cruise Line', 'Norwegian Cruise Line']
            for line in expected_cruise_lines:
                if line not in cruise_lines:
                    self.log_test("Scraping Info - Cruise Lines List", False,
                                f"Missing cruise line: {line}")
                    return False
                    
            self.log_test("Scraping Info Endpoint", True, 
                        f"10 airlines and 10 cruise lines confirmed")
            return True
            
        except Exception as e:
            self.log_test("Scraping Info Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_stats_endpoint(self):
        """Test /api/stats endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/stats", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Stats Endpoint", False,
                            f"Status code {response.status_code}", "200", str(response.status_code))
                return False
                
            data = response.json()
            
            # Check data_source
            if data.get('data_source') != 'web_scraping':
                self.log_test("Stats - Data Source", False,
                            "Wrong data source", "web_scraping", data.get('data_source'))
                return False
                
            # Check scraping targets
            scraping_targets = data.get('scraping_targets', {})
            if scraping_targets.get('airlines') != 10:
                self.log_test("Stats - Airlines Count", False,
                            "Wrong airlines count", "10", str(scraping_targets.get('airlines')))
                return False
                
            if scraping_targets.get('cruise_lines') != 10:
                self.log_test("Stats - Cruise Lines Count", False,
                            "Wrong cruise lines count", "10", str(scraping_targets.get('cruise_lines')))
                return False
                
            # Check if we have offers (should be >100 based on requirements)
            total_offers = data.get('total_offers', 0)
            if total_offers < 100:
                self.log_test("Stats - Total Offers Count", False,
                            f"Expected >100 offers, got {total_offers}")
                return False
                
            self.log_test("Stats Endpoint", True, 
                        f"Data source confirmed, {total_offers} total offers")
            return True
            
        except Exception as e:
            self.log_test("Stats Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_search_endpoint(self):
        """Test /api/search endpoint for live web scraping"""
        try:
            search_data = {
                "departure": "JFK",
                "arrival": "LAX", 
                "min_discount": 50,
                "offer_type": "all"
            }
            
            print("   Performing live web scraping search (may take 10-15 seconds)...")
            response = self.session.post(f"{self.api_url}/search", 
                                       json=search_data, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Search Endpoint", False,
                            f"Status code {response.status_code}", "200", str(response.status_code))
                return False
                
            data = response.json()
            
            # Check data_source
            if data.get('data_source') != 'live_web_scraping':
                self.log_test("Search - Data Source", False,
                            "Wrong data source", "live_web_scraping", data.get('data_source'))
                return False
                
            # Check if we got offers
            offers = data.get('offers', [])
            if len(offers) == 0:
                self.log_test("Search - Offers Count", False,
                            "No offers returned from live scraping")
                return False
                
            # Check offer structure and source_api
            sample_offer = offers[0]
            source_api = sample_offer.get('source_api', '')
            if not source_api.startswith('scraped_'):
                self.log_test("Search - Source API Format", False,
                            "source_api should start with 'scraped_'", "scraped_*", source_api)
                return False
                
            self.log_test("Search Endpoint", True, 
                        f"Live scraping returned {len(offers)} offers")
            return True
            
        except Exception as e:
            self.log_test("Search Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_offers_endpoint(self):
        """Test /api/offers endpoint"""
        try:
            params = {
                'offer_type': 'all',
                'min_discount': 50,
                'limit': 20
            }
            
            response = self.session.get(f"{self.api_url}/offers", params=params, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Offers Endpoint", False,
                            f"Status code {response.status_code}", "200", str(response.status_code))
                return False
                
            data = response.json()
            
            # Check data_source
            if data.get('data_source') != 'web_scraped_data':
                self.log_test("Offers - Data Source", False,
                            "Wrong data source", "web_scraped_data", data.get('data_source'))
                return False
                
            # Check offers structure
            offers = data.get('offers', [])
            if len(offers) > 0:
                sample_offer = offers[0]
                source_api = sample_offer.get('source_api', '')
                if not source_api.startswith('scraped_'):
                    self.log_test("Offers - Source API Format", False,
                                "source_api should start with 'scraped_'", "scraped_*", source_api)
                    return False
                    
            self.log_test("Offers Endpoint", True, 
                        f"Retrieved {len(offers)} scraped offers")
            return True
            
        except Exception as e:
            self.log_test("Offers Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_flight_specific_search(self):
        """Test flight-specific search"""
        try:
            search_data = {
                "departure": "JFK",
                "arrival": "LHR",
                "min_discount": 60,
                "offer_type": "flight"
            }
            
            print("   Testing flight-specific scraping...")
            response = self.session.post(f"{self.api_url}/search", 
                                       json=search_data, timeout=25)
            
            if response.status_code != 200:
                self.log_test("Flight Search", False,
                            f"Status code {response.status_code}")
                return False
                
            data = response.json()
            offers = data.get('offers', [])
            
            # All offers should be flights
            for offer in offers:
                if offer.get('type') != 'flight':
                    self.log_test("Flight Search - Type Filter", False,
                                "Non-flight offer in flight search")
                    return False
                    
            self.log_test("Flight Search", True, 
                        f"Flight-only search returned {len(offers)} flight offers")
            return True
            
        except Exception as e:
            self.log_test("Flight Search", False, f"Exception: {str(e)}")
            return False

    def test_cruise_specific_search(self):
        """Test cruise-specific search"""
        try:
            search_data = {
                "min_discount": 55,
                "offer_type": "cruise"
            }
            
            print("   Testing cruise-specific scraping...")
            response = self.session.post(f"{self.api_url}/search", 
                                       json=search_data, timeout=25)
            
            if response.status_code != 200:
                self.log_test("Cruise Search", False,
                            f"Status code {response.status_code}")
                return False
                
            data = response.json()
            offers = data.get('offers', [])
            
            # All offers should be cruises
            for offer in offers:
                if offer.get('type') != 'cruise':
                    self.log_test("Cruise Search - Type Filter", False,
                                "Non-cruise offer in cruise search")
                    return False
                    
            self.log_test("Cruise Search", True, 
                        f"Cruise-only search returned {len(offers)} cruise offers")
            return True
            
        except Exception as e:
            self.log_test("Cruise Search", False, f"Exception: {str(e)}")
            return False

    def test_offer_authenticity_validation(self):
        """Test AI authenticity validation"""
        try:
            # Get some offers to check validation
            response = self.session.get(f"{self.api_url}/offers?limit=5", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Authenticity Validation", False, "Could not get offers for validation test")
                return False
                
            data = response.json()
            offers = data.get('offers', [])
            
            if len(offers) == 0:
                self.log_test("Authenticity Validation", False, "No offers to validate")
                return False
                
            # Check if offers have validation fields
            validated_offers = 0
            for offer in offers:
                if 'is_authentic' in offer and 'validation_timestamp' in offer:
                    validated_offers += 1
                    
            if validated_offers == 0:
                self.log_test("Authenticity Validation", False, "No offers have validation fields")
                return False
                
            self.log_test("Authenticity Validation", True, 
                        f"{validated_offers}/{len(offers)} offers have AI validation")
            return True
            
        except Exception as e:
            self.log_test("Authenticity Validation", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Volo Web Scraping Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Core endpoint tests
        self.test_health_endpoint()
        self.test_scraping_info_endpoint()
        self.test_stats_endpoint()
        
        # Search functionality tests
        self.test_search_endpoint()
        self.test_offers_endpoint()
        
        # Specific search tests
        self.test_flight_specific_search()
        self.test_cruise_specific_search()
        
        # Validation tests
        self.test_offer_authenticity_validation()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['test']}")
                if test['details']:
                    print(f"   {test['details']}")
        
        return len(self.failed_tests) == 0

def main():
    tester = VoloWebScrapingTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())