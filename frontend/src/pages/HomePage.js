import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import SearchBar from "@/components/SearchBar";
import DealCard from "@/components/DealCard";
import StatsBar from "@/components/StatsBar";
import FilterSidebar from "@/components/FilterSidebar";
import { toast } from "sonner";
import { Plane, Ship, TrendingDown } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function HomePage() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    offerType: "all",
    minDiscount: 50,
    sortBy: "discount"
  });

  const fetchOffers = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/offers`, {
        params: {
          offer_type: filters.offerType,
          min_discount: filters.minDiscount,
          limit: 50
        }
      });
      setOffers(response.data.offers || []);
    } catch (error) {
      console.error("Error fetching offers:", error);
      toast.error("Failed to load offers");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const handleSearch = async (searchParams) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/search`, searchParams);
      setOffers(response.data.offers || []);
      toast.success(`Found ${response.data.total_results} deals!`);
    } catch (error) {
      console.error("Search error:", error);
      toast.error("Search failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOffers();
    fetchStats();
    
    // Refresh offers every 5 minutes
    const interval = setInterval(() => {
      fetchOffers();
      fetchStats();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [fetchOffers]);

  return (
    <div className="min-h-screen bg-slate-50" data-testid="home-page">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-slate-900 text-white" data-testid="hero-section">
        <div className="hero-glow absolute inset-0"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center space-y-6">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-heading" data-testid="hero-title">
              Volo
            </h1>
            <p className="text-xl sm:text-2xl text-slate-300 max-w-3xl mx-auto" data-testid="hero-tagline">
              The Truth Radar for Travel Deals
            </p>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto" data-testid="hero-description">
              Discover verified travel deals with 50-90% discounts. Real-time tracking across airlines and cruise lines.
            </p>
            
            {stats && (
              <div className="flex justify-center gap-8 pt-8" data-testid="hero-stats">
                <div className="text-center">
                  <div className="text-4xl font-bold text-orange-500" data-testid="total-offers">{stats.total_offers}</div>
                  <div className="text-sm text-slate-400">Active Deals</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-emerald-500" data-testid="max-discount">{Math.max(stats.max_flight_discount, stats.max_cruise_discount)}%</div>
                  <div className="text-sm text-slate-400">Max Discount</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-500" data-testid="avg-discount">
                    {Math.round((stats.flight_avg_discount + stats.cruise_avg_discount) / 2)}%
                  </div>
                  <div className="text-sm text-slate-400">Avg Discount</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8" data-testid="search-section">
        <SearchBar onSearch={handleSearch} />
      </div>

      {/* Stats Bar */}
      {stats && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="stats-bar">
          <StatsBar stats={stats} />
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12" data-testid="main-content">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-64 flex-shrink-0" data-testid="filters-sidebar">
            <FilterSidebar filters={filters} onFilterChange={setFilters} />
          </div>

          {/* Deals Grid */}
          <div className="flex-1" data-testid="deals-grid">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold font-heading text-slate-900" data-testid="deals-title">
                {filters.offerType === "flight" && "Flight Deals"}
                {filters.offerType === "cruise" && "Cruise Deals"}
                {filters.offerType === "all" && "All Deals"}
              </h2>
              <div className="text-sm text-slate-600" data-testid="deals-count">
                {offers.length} deals found
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64" data-testid="loading-spinner">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : offers.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-xl shadow-sm" data-testid="no-deals">
                <TrendingDown className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 text-lg">No deals found matching your criteria</p>
                <p className="text-slate-400 text-sm mt-2">Try adjusting your filters</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6" data-testid="deals-list">
                {offers.map((offer, index) => (
                  <DealCard 
                    key={offer.id} 
                    offer={offer} 
                    className={`fade-up stagger-${Math.min(index % 4 + 1, 4)}`}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}