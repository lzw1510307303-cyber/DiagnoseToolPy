import { Result, Button } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';

function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  return (
    <div>
      <h1>Task Detail</h1>
      <Result
        status="info"
        title="Under Development"
        subTitle={`Task detail page for task: ${taskId || 'unknown'}`}
        extra={
          <Button type="primary" onClick={() => navigate('/analysis')}>
            Back to Analysis
          </Button>
        }
      />
    </div>
  );
}

export default TaskDetailPage;
