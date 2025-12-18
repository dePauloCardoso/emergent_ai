import { ExternalLink, CheckCircle, Plane, Ship, Clock, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";

export const DealCard = ({ offer, className = "" }) => {
  const isFlightOffer = offer.type === "flight";
  
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), "MMM dd, yyyy");
    } catch {
      return dateString;
    }
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  return (
    <div
      className={`bg-white rounded-xl overflow-hidden hover:shadow-xl border border-slate-200 hover:border-blue-300 transition-all duration-300 group relative hover-lift ${className}`}
      data-testid="deal-card"
    >
      {/* Main Content */}
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Left Section - Details */}
          <div className="flex-1 space-y-3">
            {/* Header */}
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-50 rounded-lg" data-testid="offer-icon">
                {isFlightOffer ? (
                  <Plane className="w-6 h-6 text-blue-600" />
                ) : (
                  <Ship className="w-6 h-6 text-blue-600" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-xl font-bold text-slate-900 font-heading" data-testid="offer-title">
                    {isFlightOffer ? offer.airline : offer.cruise_line}
                  </h3>
                  {offer.is_authentic && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200" data-testid="verified-badge">
                      <CheckCircle className="w-3 h-3" />
                      VERIFIED
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <span className="font-mono text-xs px-2 py-0.5 bg-slate-100 rounded" data-testid="source-badge">
                    {offer.source_api}
                  </span>
                  {isFlightOffer && (
                    <span className="font-mono" data-testid="flight-number">{offer.flight_number}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Route/Details */}
            <div className="flex items-center gap-4 text-sm" data-testid="offer-details">
              {isFlightOffer ? (
                <>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span className="font-mono font-semibold text-slate-900" data-testid="departure">
                      {offer.departure_airport}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400">
                    <Clock className="w-4 h-4" />
                    <span data-testid="duration">{formatDuration(offer.duration_minutes)}</span>
                    <span>({offer.stops} stop{offer.stops !== 1 ? 's' : ''})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">→</span>
                    <span className="font-mono font-semibold text-slate-900" data-testid="arrival">
                      {offer.arrival_airport}
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span className="font-semibold text-slate-900" data-testid="departure-port">
                      {offer.departure_port}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-600">
                    <Clock className="w-4 h-4" />
                    <span data-testid="cruise-duration">{offer.duration_nights} nights</span>
                  </div>
                  <div className="px-2 py-1 bg-slate-100 rounded text-slate-700 text-xs" data-testid="cabin-type">
                    {offer.cabin_type}
                  </div>
                </>
              )}
            </div>

            {/* Date */}
            <div className="text-sm text-slate-600" data-testid="departure-date">
              Departs: {formatDate(offer.departure_date)}
            </div>
          </div>

          {/* Right Section - Pricing */}
          <div className="flex flex-col items-end gap-3 min-w-[180px]">
            <div className="text-right">
              <div className="text-sm text-slate-500 line-through" data-testid="original-price">
                ${offer.original_price.toFixed(2)}
              </div>
              <div className="text-3xl font-bold text-slate-900 font-heading" data-testid="current-price">
                ${offer.current_price.toFixed(2)}
              </div>
            </div>

            <div className="px-4 py-2 bg-orange-500 text-white rounded-md font-bold text-sm uppercase tracking-wider shadow-md shadow-orange-500/20" data-testid="discount-badge">
              {offer.discount_percentage.toFixed(0)}% OFF
            </div>

            <Button
              asChild
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-full font-semibold shadow-lg shadow-blue-600/20 hover:scale-105 active:scale-95 transition-all"
              data-testid="book-now-button"
            >
              <a href={offer.booking_link} target="_blank" rel="noopener noreferrer">
                Book Now
                <ExternalLink className="ml-2 w-4 h-4" />
              </a>
            </Button>
          </div>
        </div>
      </div>

      {/* Ticket Stub */}
      <div className="relative bg-slate-50 border-t border-dashed border-slate-300 px-6 py-3 flex justify-between items-center text-xs text-slate-600" data-testid="ticket-stub">
        <div>
          ID: <span className="font-mono" data-testid="offer-id">{offer.id.substring(0, 8)}</span>
        </div>
        <div data-testid="validation-timestamp">
          Validated: {formatDate(offer.validation_timestamp)}
        </div>
      </div>
    </div>
  );
};

export default DealCard;