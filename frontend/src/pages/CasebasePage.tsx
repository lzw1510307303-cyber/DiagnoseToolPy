import { Result, Button } from 'antd';

function CasebasePage() {
  return (
    <div>
      <h1>Casebase</h1>
      <Result
        status="info"
        title="Under Development"
        subTitle="Case list and search functionality coming soon"
        extra={
          <Button type="primary" href="/">
            Go to Dashboard
          </Button>
        }
      />
    </div>
  );
}

export default CasebasePage;
