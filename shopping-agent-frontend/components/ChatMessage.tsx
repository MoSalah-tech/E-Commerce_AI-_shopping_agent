import { RecommendationCard, Recommendation } from "./RecommendationCard";

export type Message = {
  id: string;
  role: "user" | "assistant";
  text?: string;
  recommendations?: Recommendation[];
};

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] ${isUser ? "" : "w-full"}`}>
        {message.text && (
          <div
            className={
              isUser
                ? "bg-ink text-paper rounded-sm px-4 py-2.5 font-body text-[15px] leading-relaxed"
                : "font-body text-[15px] leading-relaxed text-ink px-1"
            }
          >
            {message.text}
          </div>
        )}

        {message.recommendations && message.recommendations.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-3">
            {message.recommendations.map((item, i) => (
              <RecommendationCard key={i} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}