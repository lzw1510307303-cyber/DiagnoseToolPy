import { Result, Button } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';

function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  return (
    <div>
      <h1>Case Detail</h1>
      <Result
        status="info"
        title="Under Development"
        subTitle={`Case detail page for case: ${caseId || 'unknown'}`}
        extra={
          <Button type="primary" onClick={() => navigate('/cases')}>
            Back to Casebase
          </Button>
        }
      />
    </div>
  );
}

export default CaseDetailPage;
