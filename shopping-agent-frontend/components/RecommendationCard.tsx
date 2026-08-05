export type Recommendation = {
  product_name: string;
  reason: string;
  purchase_link?: string | null;
  price?: string | null;
  source?: string | null;
};

export function RecommendationCard({ item }: { item: Recommendation }) {
  return (
    <div className="ticket-edge bg-paper-raised border border-hairline rounded-sm px-4 pt-4 pb-6 shadow-sm max-w-sm">
      <div className="flex items-start justify-between gap-3 dotted-rule pb-3 mb-3">
        <div>
          <p className="font-display text-base leading-snug text-ink">{item.product_name}</p>
          {item.source && (
            <p className="font-mono text-[11px] uppercase tracking-wide text-ink-soft mt-1">
              {item.source}
            </p>
          )}
        </div>
        {item.price && (
          <p className="font-mono text-rust text-lg whitespace-nowrap">{item.price}</p>
        )}
      </div>

      <p className="text-sm text-ink-soft leading-relaxed mb-3">{item.reason}</p>

      {item.purchase_link && (
        <a  
          href={item.purchase_link}
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono text-xs text-moss hover:text-moss-deep underline underline-offset-2"
        >
          View item →
        </a>
      )}
    </div>
  );
}