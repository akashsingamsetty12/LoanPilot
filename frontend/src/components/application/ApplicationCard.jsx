/** ApplicationCard — Summary card for dashboard list."""
import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';

export default function ApplicationCard({ application }) {
  // TODO: Design the application summary card
  return (
    <Link to={`/applications/${application?.id}`} className="block border rounded-lg p-4 hover:shadow">
      <h3>{application?.applicant_name || 'Loading...'}</h3>
      <StatusBadge status={application?.status || 'created'} />
      <p>Document count, risk level, date</p>
    </Link>
  );
}
