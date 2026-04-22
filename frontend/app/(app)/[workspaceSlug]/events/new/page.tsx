export default function NewEventPage() {
  return (
    <section className="atelier-stack">
      <header className="atelier-pagehead row">
        <div>
          <small>Events</small>
          <h1>Create New Event</h1>
          <p>Build and publish your event page in one flow.</p>
        </div>
      </header>

      <div className="fund-grid two-rail">
        <article className="atelier-card">
          <h3>Event Details</h3>
          <form className="form-stack">
            <label>
              Event title
              <input type="text" placeholder="Annual Department Dinner" />
            </label>

            <div className="form-two">
              <label>
                Event type
                <select defaultValue="social">
                  <option value="social">Social</option>
                  <option value="academic">Academic</option>
                  <option value="professional">Professional</option>
                  <option value="fundraiser">Fundraiser</option>
                </select>
              </label>
              <label>
                Venue
                <input type="text" placeholder="Main Hall" />
              </label>
            </div>

            <div className="form-two">
              <label>
                Date
                <input type="date" />
              </label>
              <label>
                Time
                <input type="time" />
              </label>
            </div>

            <label>
              Description
              <textarea rows={5} placeholder="Tell members what this event is about" />
            </label>

            <div className="form-actions">
              <button className="atelier-btn-secondary" type="button">
                Save Draft
              </button>
              <button className="atelier-btn-primary" type="submit">
                Create Event
              </button>
            </div>
          </form>
        </article>

        <article className="atelier-card preview-card">
          <h3>Live Preview</h3>
          <div className="event-preview">
            <div className="preview-pill">Social Event</div>
            <h4>Annual Department Dinner</h4>
            <p>Main Hall - 7:00 PM</p>
            <p>Dress code: formal. Awards and recognition for graduating class.</p>
          </div>
          <div className="note-item">
            <strong>Tip</strong>
            <p>Add a clear title and date first. Most RSVP decisions come from those two fields.</p>
          </div>
        </article>
      </div>
    </section>
  );
}
