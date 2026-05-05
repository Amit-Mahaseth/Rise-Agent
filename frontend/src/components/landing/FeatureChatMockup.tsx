export function FeatureChatMockup() {
  return (
    <div className="chat-mockup">
      <div className="chat-mockup__head">
        <span className="chat-mockup__dot" />
        <span>Voice session · North desk</span>
      </div>
      <div className="chat-mockup__thread">
        <div className="chat-mockup__row chat-mockup__row--agent">
          <p>Hi Priya—calling about your personal loan application. Is now a good time?</p>
        </div>
        <div className="chat-mockup__row chat-mockup__row--user">
          <p>Yes, go ahead.</p>
        </div>
        <div className="chat-mockup__row chat-mockup__row--agent">
          <p>Great. I can walk through eligibility and documents, or send a WhatsApp pack—what works better?</p>
        </div>
        <div className="chat-mockup__row chat-mockup__row--user">
          <p>WhatsApp is easier.</p>
        </div>
      </div>
    </div>
  );
}
