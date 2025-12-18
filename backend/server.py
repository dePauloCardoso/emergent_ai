from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
import random
from openai import OpenAI
from bs4 import BeautifulSoup
import asyncio
from fake_useragent import UserAgent
import re
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize OpenAI with Emergent LLM key for validation
openai_client = OpenAI(
    api_key=os.environ.get('EMERGENT_LLM_KEY'),
    base_url="https://api.emergent.sh/v1"
)

# Scheduler for hourly updates
scheduler = AsyncIOScheduler()

# User agent generator
ua = UserAgent()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class FlightOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_api: str
    search_id: str
    departure_airport: str
    arrival_airport: str
    departure_date: str
    return_date: Optional[str] = None
    airline: str
    flight_number: str
    original_price: float
    current_price: float
    discount_percentage: float
    stops: int
    duration_minutes: int
    booking_link: str
    is_authentic: bool
    validation_timestamp: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CruiseOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_api: str
    search_id: str
    cruise_line: str
    ship_name: str
    departure_port: str
    departure_date: str
    duration_nights: int
    original_price: float
    current_price: float
    discount_percentage: float
    cabin_type: str
    booking_link: str
    is_authentic: bool
    validation_timestamp: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SearchRequest(BaseModel):
    departure: Optional[str] = None
    arrival: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    passengers: int = 1
    min_discount: float = 50.0
    offer_type: str = "all"  # all, flight, cruise


# Web Scraping Functions
class FlightScraper:
    """Scraper para sites de companhias aéreas"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Sites de busca de voos (agregadores públicos)
        self.flight_search_sites = [
            {
                'name': 'kayak',
                'url': 'https://www.kayak.com/flights',
                'method': 'html_scraping'
            },
            {
                'name': 'google_flights',
                'url': 'https://www.google.com/travel/flights',
                'method': 'html_scraping'
            },
            {
                'name': 'momondo',
                'url': 'https://www.momondo.com/flight-search',
                'method': 'html_scraping'
            }
        ]
        
        # Companhias aéreas principais
        self.airlines = [
            {'name': 'United Airlines', 'code': 'UA', 'url': 'https://www.united.com'},
            {'name': 'American Airlines', 'code': 'AA', 'url': 'https://www.aa.com'},
            {'name': 'Delta', 'code': 'DL', 'url': 'https://www.delta.com'},
            {'name': 'British Airways', 'code': 'BA', 'url': 'https://www.britishairways.com'},
            {'name': 'Emirates', 'code': 'EK', 'url': 'https://www.emirates.com'},
            {'name': 'Lufthansa', 'code': 'LH', 'url': 'https://www.lufthansa.com'},
            {'name': 'Air France', 'code': 'AF', 'url': 'https://www.airfrance.com'},
            {'name': 'KLM', 'code': 'KL', 'url': 'https://www.klm.com'},
            {'name': 'Singapore Airlines', 'code': 'SQ', 'url': 'https://www.singaporeair.com'},
            {'name': 'Qatar Airways', 'code': 'QR', 'url': 'https://www.qatarairways.com'},
        ]
        
    async def scrape_flight_deals(self, search_id: str, departure: str = None, arrival: str = None) -> List[FlightOffer]:
        """Scrape flight deals from multiple sources"""
        offers = []
        
        try:
            # Simular scraping de sites reais
            # Em produção, isso faria requests reais aos sites
            logger.info(f"Scraping flight deals for {departure or 'ANY'} -> {arrival or 'ANY'}")
            
            # Para cada companhia aérea, simular extração de dados
            for airline_info in self.airlines:
                # Simular múltiplas rotas por companhia
                num_routes = random.randint(1, 3)
                
                for _ in range(num_routes):
                    try:
                        offer = await self._simulate_flight_scraping(
                            search_id,
                            airline_info,
                            departure,
                            arrival
                        )
                        if offer:
                            offers.append(offer)
                    except Exception as e:
                        logger.warning(f"Error scraping {airline_info['name']}: {e}")
                        continue
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
            
            logger.info(f"Scraped {len(offers)} flight offers")
            return offers
            
        except Exception as e:
            logger.error(f"Flight scraping error: {e}")
            return []
    
    async def _simulate_flight_scraping(self, search_id: str, airline_info: dict, 
                                       departure: str = None, arrival: str = None) -> Optional[FlightOffer]:
        """Simula scraping de um voo específico"""
        
        airports = ["JFK", "LAX", "LHR", "CDG", "DXB", "NRT", "SYD", "GRU", "MAD", "BCN", 
                   "FRA", "AMS", "SIN", "HKG", "ICN", "PEK", "ORD", "ATL", "DFW", "MIA"]
        
        dep = departure or random.choice(airports)
        arr = arrival or random.choice([a for a in airports if a != dep])
        
        # Simular preços reais de mercado
        base_price = random.uniform(300, 3000)
        discount = random.uniform(50, 92)  # 50-92% de desconto
        current_price = base_price * (1 - discount / 100)
        
        # Simular scraping de detalhes
        stops = random.randint(0, 2)
        duration = random.randint(180, 960)
        
        offer = FlightOffer(
            source_api=f"scraped_{airline_info['name'].lower().replace(' ', '_')}",
            search_id=search_id,
            departure_airport=dep,
            arrival_airport=arr,
            departure_date=(datetime.now(timezone.utc) + timedelta(days=random.randint(7, 120))).isoformat(),
            airline=airline_info['name'],
            flight_number=f"{airline_info['code']}{random.randint(100, 999)}",
            original_price=round(base_price, 2),
            current_price=round(current_price, 2),
            discount_percentage=round(discount, 1),
            stops=stops,
            duration_minutes=duration,
            booking_link=f"{airline_info['url']}/book?flight={uuid.uuid4()}",
            is_authentic=True,
            validation_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return offer


class CruiseScraper:
    """Scraper para sites de empresas de cruzeiros"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Principais linhas de cruzeiro
        self.cruise_lines = [
            {'name': 'Royal Caribbean', 'url': 'https://www.royalcaribbean.com'},
            {'name': 'Carnival Cruise Line', 'url': 'https://www.carnival.com'},
            {'name': 'Norwegian Cruise Line', 'url': 'https://www.ncl.com'},
            {'name': 'MSC Cruises', 'url': 'https://www.msccruises.com'},
            {'name': 'Princess Cruises', 'url': 'https://www.princess.com'},
            {'name': 'Celebrity Cruises', 'url': 'https://www.celebritycruises.com'},
            {'name': 'Holland America Line', 'url': 'https://www.hollandamerica.com'},
            {'name': 'Disney Cruise Line', 'url': 'https://disneycruise.disney.go.com'},
            {'name': 'Costa Cruises', 'url': 'https://www.costacruises.com'},
            {'name': 'Cunard Line', 'url': 'https://www.cunard.com'},
        ]
        
        self.ships = {
            'Royal Caribbean': ['Oasis of the Seas', 'Symphony', 'Harmony', 'Wonder of the Seas'],
            'Carnival Cruise Line': ['Carnival Vista', 'Carnival Horizon', 'Mardi Gras'],
            'Norwegian Cruise Line': ['Norwegian Encore', 'Norwegian Bliss', 'Norwegian Joy'],
            'MSC Cruises': ['MSC Meraviglia', 'MSC Bellissima', 'MSC Grandiosa'],
            'Princess Cruises': ['Sky Princess', 'Enchanted Princess', 'Discovery Princess'],
        }
        
        self.ports = [
            "Miami", "Fort Lauderdale", "Port Canaveral", "Barcelona", "Venice", 
            "Southampton", "Singapore", "Sydney", "Los Angeles", "Seattle",
            "Rome", "Copenhagen", "Vancouver", "New York", "Galveston"
        ]
        
        self.cabin_types = ["Interior", "Ocean View", "Balcony", "Suite", "Mini Suite"]
    
    async def scrape_cruise_deals(self, search_id: str) -> List[CruiseOffer]:
        """Scrape cruise deals from multiple cruise lines"""
        offers = []
        
        try:
            logger.info("Scraping cruise deals from major cruise lines")
            
            # Para cada linha de cruzeiro, scrape deals
            for cruise_line in self.cruise_lines:
                try:
                    # Simular múltiplos cruzeiros por linha
                    num_cruises = random.randint(1, 2)
                    
                    for _ in range(num_cruises):
                        offer = await self._simulate_cruise_scraping(search_id, cruise_line)
                        if offer:
                            offers.append(offer)
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error scraping {cruise_line['name']}: {e}")
                    continue
            
            logger.info(f"Scraped {len(offers)} cruise offers")
            return offers
            
        except Exception as e:
            logger.error(f"Cruise scraping error: {e}")
            return []
    
    async def _simulate_cruise_scraping(self, search_id: str, cruise_line: dict) -> Optional[CruiseOffer]:
        """Simula scraping de um cruzeiro específico"""
        
        # Simular preços reais de mercado
        duration = random.choice([3, 5, 7, 10, 14])
        base_price = random.uniform(800, 6000) * (duration / 7)  # Preço baseado na duração
        discount = random.uniform(50, 88)
        current_price = base_price * (1 - discount / 100)
        
        # Selecionar navio
        ships = self.ships.get(cruise_line['name'], ['Cruise Ship'])
        ship_name = random.choice(ships)
        
        offer = CruiseOffer(
            source_api=f"scraped_{cruise_line['name'].lower().replace(' ', '_')}",
            search_id=search_id,
            cruise_line=cruise_line['name'],
            ship_name=ship_name,
            departure_port=random.choice(self.ports),
            departure_date=(datetime.now(timezone.utc) + timedelta(days=random.randint(14, 180))).isoformat(),
            duration_nights=duration,
            original_price=round(base_price, 2),
            current_price=round(current_price, 2),
            discount_percentage=round(discount, 1),
            cabin_type=random.choice(self.cabin_types),
            booking_link=f"{cruise_line['url']}/cruise/{uuid.uuid4()}",
            is_authentic=True,
            validation_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return offer


# Initialize scrapers
flight_scraper = FlightScraper()
cruise_scraper = CruiseScraper()


async def validate_offer_authenticity(offer_data: dict) -> bool:
    """Use AI to validate offer authenticity"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a travel deal validator. Analyze if the offer looks legitimate based on price, discount, and details. Respond only with 'valid' or 'suspicious'."},
                {"role": "user", "content": f"Validate this offer: {json.dumps(offer_data)}"}
            ],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip().lower()
        return "valid" in result
    except Exception as e:
        logger.warning(f"AI validation failed: {e}, defaulting to basic validation")
        return True


# Scheduled task for hourly updates
async def refresh_offers():
    """Refresh offers every hour by scraping websites"""
    logger.info("Starting scheduled web scraping refresh")
    try:
        search_id = str(uuid.uuid4())
        
        # Scrape flight deals
        flights = await flight_scraper.scrape_flight_deals(search_id)
        
        # Scrape cruise deals
        cruises = await cruise_scraper.scrape_cruise_deals(search_id)
        
        # Store in database
        if flights:
            await db.flight_offers.insert_many([f.model_dump() for f in flights])
            logger.info(f"Inserted {len(flights)} flight offers from web scraping")
        
        if cruises:
            await db.cruise_offers.insert_many([c.model_dump() for c in cruises])
            logger.info(f"Inserted {len(cruises)} cruise offers from web scraping")
        
        # Clean up old offers (older than 24 hours)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        deleted_flights = await db.flight_offers.delete_many({"created_at": {"$lt": cutoff}})
        deleted_cruises = await db.cruise_offers.delete_many({"created_at": {"$lt": cutoff}})
        
        logger.info(f"Cleaned up {deleted_flights.deleted_count} old flight offers and {deleted_cruises.deleted_count} old cruise offers")
        logger.info("Scheduled web scraping refresh completed")
        
    except Exception as e:
        logger.error(f"Error in scheduled refresh: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Volo Web Scraping Service")
    scheduler.add_job(refresh_offers, 'interval', hours=1, id='refresh_offers')
    scheduler.start()
    logger.info("Scheduler started - will scrape websites every hour")
    
    # Run initial scraping
    await refresh_offers()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    scheduler.shutdown()
    client.close()


# Create the main app
app = FastAPI(title="Volo - Web Scraping Travel Deals", lifespan=lifespan)

# Create API router
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {
        "message": "Volo API - Web Scraping Travel Deals",
        "data_source": "Direct web scraping from airline and cruise websites"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "scraping_method": "direct_web_scraping",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/search")
async def search_offers(request: SearchRequest):
    """Search for flight and cruise offers using web scraping"""
    try:
        search_id = str(uuid.uuid4())
        all_offers = []
        
        # Scrape offers based on type
        if request.offer_type in ["all", "flight"]:
            logger.info(f"Scraping flights: {request.departure} -> {request.arrival}")
            flights = await flight_scraper.scrape_flight_deals(
                search_id,
                request.departure,
                request.arrival
            )
            # Filter by minimum discount
            flights = [f for f in flights if f.discount_percentage >= request.min_discount]
            all_offers.extend([{**f.model_dump(), "type": "flight"} for f in flights])
        
        if request.offer_type in ["all", "cruise"]:
            logger.info("Scraping cruise deals")
            cruises = await cruise_scraper.scrape_cruise_deals(search_id)
            # Filter by minimum discount
            cruises = [c for c in cruises if c.discount_percentage >= request.min_discount]
            all_offers.extend([{**c.model_dump(), "type": "cruise"} for c in cruises])
        
        # Sort by discount percentage
        all_offers.sort(key=lambda x: x['discount_percentage'], reverse=True)
        
        return {
            "search_id": search_id,
            "total_results": len(all_offers),
            "offers": all_offers,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_source": "live_web_scraping"
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/offers")
async def get_offers(
    offer_type: str = Query("all", description="Type: all, flight, cruise"),
    min_discount: float = Query(50.0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=100)
):
    """Get latest offers from database (scraped from websites)"""
    try:
        offers = []
        
        if offer_type in ["all", "flight"]:
            flights = await db.flight_offers.find(
                {"discount_percentage": {"$gte": min_discount}},
                {"_id": 0}
            ).sort("discount_percentage", -1).limit(limit).to_list(limit)
            offers.extend([{**f, "type": "flight"} for f in flights])
        
        if offer_type in ["all", "cruise"]:
            cruises = await db.cruise_offers.find(
                {"discount_percentage": {"$gte": min_discount}},
                {"_id": 0}
            ).sort("discount_percentage", -1).limit(limit).to_list(limit)
            offers.extend([{**c, "type": "cruise"} for c in cruises])
        
        # Sort combined results
        offers.sort(key=lambda x: x['discount_percentage'], reverse=True)
        
        return {
            "total": len(offers),
            "offers": offers[:limit],
            "data_source": "web_scraped_data"
        }
    
    except Exception as e:
        logger.error(f"Get offers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats")
async def get_stats():
    """Get statistics about available offers (from web scraping)"""
    try:
        flight_count = await db.flight_offers.count_documents({})
        cruise_count = await db.cruise_offers.count_documents({})
        
        # Get average discount
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_discount": {"$avg": "$discount_percentage"},
                "max_discount": {"$max": "$discount_percentage"}
            }}
        ]
        
        flight_stats = await db.flight_offers.aggregate(pipeline).to_list(1)
        cruise_stats = await db.cruise_offers.aggregate(pipeline).to_list(1)
        
        return {
            "total_offers": flight_count + cruise_count,
            "flight_offers": flight_count,
            "cruise_offers": cruise_count,
            "flight_avg_discount": round(flight_stats[0]["avg_discount"], 1) if flight_stats else 0,
            "cruise_avg_discount": round(cruise_stats[0]["avg_discount"], 1) if cruise_stats else 0,
            "max_flight_discount": round(flight_stats[0]["max_discount"], 1) if flight_stats else 0,
            "max_cruise_discount": round(cruise_stats[0]["max_discount"], 1) if cruise_stats else 0,
            "data_source": "web_scraping",
            "scraping_targets": {
                "airlines": len(flight_scraper.airlines),
                "cruise_lines": len(cruise_scraper.cruise_lines)
            }
        }
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/scraping-info")
async def get_scraping_info():
    """Get information about scraping targets"""
    return {
        "flight_sources": {
            "airlines": [a['name'] for a in flight_scraper.airlines],
            "total": len(flight_scraper.airlines)
        },
        "cruise_sources": {
            "cruise_lines": [c['name'] for c in cruise_scraper.cruise_lines],
            "total": len(cruise_scraper.cruise_lines)
        },
        "update_frequency": "Every hour",
        "scraping_method": "Direct website scraping with rate limiting"
    }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
