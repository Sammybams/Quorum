import { apiGet } from "@/lib/api";

type EventPublic = {
  title: string;
  slug: string;
  event_type: string;
  starts_at: string;
  venue?: string;
  description?: string;
  rsvp_enabled: boolean;
  rsvp_count: number;
};

export default async function PublicEventPage({ params }: { params: { eventSlug: string } }) {
  const event = await apiGet<EventPublic>(`/public/e/${params.eventSlug}`);

  return (
    <main>
      <div className="hero">
        <h1>{event.title}</h1>
        <p>{event.starts_at} {event.venue ? `• ${event.venue}` : ""}</p>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <p>{event.description || "No description provided."}</p>
        <p className="muted">RSVPs: {event.rsvp_count}</p>
      </div>
    </main>
  );
}
