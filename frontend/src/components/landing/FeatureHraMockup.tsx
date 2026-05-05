export function FeatureHraMockup() {
  return (
    <div className="hra-mockup">
      <div className="hra-mockup__phone">
        <div className="hra-mockup__chat">
          <div className="hra-mockup__bubble hra-mockup__bubble--in">Rate check requested</div>
          <div className="hra-mockup__bubble hra-mockup__bubble--out">Shared FAQ + eligibility doc</div>
        </div>
        <div className="hra-mockup__card hra-mockup__card--1">
          <span className="hra-mockup__tag">KYC-1028</span>
          <strong>Identity</strong>
          <p>Verified · eAadhaar</p>
        </div>
        <div className="hra-mockup__card hra-mockup__card--2">
          <span className="hra-mockup__tag">HRA-2041</span>
          <strong>Risk</strong>
          <p>Medium · stable income</p>
        </div>
        <div className="hra-mockup__card hra-mockup__card--3">
          <span className="hra-mockup__tag">Member</span>
          <strong>Segment</strong>
          <p>Prime · returning</p>
        </div>
      </div>
    </div>
  );
}
