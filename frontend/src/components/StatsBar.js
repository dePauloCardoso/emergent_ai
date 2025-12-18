import { TrendingDown, Plane, Ship } from "lucide-react";

export const StatsBar = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4" data-testid="stats-bar">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200" data-testid="flight-stats">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Plane className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="font-semibold text-slate-900">Flight Deals</h3>
        </div>
        <div className="space-y-1">
          <div className="text-3xl font-bold text-slate-900 font-heading" data-testid="flight-count">
            {stats.flight_offers}
          </div>
          <div className="text-sm text-slate-600">
            Avg discount: <span className="font-semibold text-orange-600" data-testid="flight-avg-discount">{stats.flight_avg_discount}%</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200" data-testid="cruise-stats">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Ship className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="font-semibold text-slate-900">Cruise Deals</h3>
        </div>
        <div className="space-y-1">
          <div className="text-3xl font-bold text-slate-900 font-heading" data-testid="cruise-count">
            {stats.cruise_offers}
          </div>
          <div className="text-sm text-slate-600">
            Avg discount: <span className="font-semibold text-orange-600" data-testid="cruise-avg-discount">{stats.cruise_avg_discount}%</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200" data-testid="best-deal-stats">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-orange-50 rounded-lg">
            <TrendingDown className="w-5 h-5 text-orange-600" />
          </div>
          <h3 className="font-semibold text-slate-900">Best Discount</h3>
        </div>
        <div className="space-y-1">
          <div className="text-3xl font-bold text-orange-600 font-heading" data-testid="max-discount-value">
            {Math.max(stats.max_flight_discount, stats.max_cruise_discount).toFixed(0)}%
          </div>
          <div className="text-sm text-slate-600">
            Available now!
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsBar;