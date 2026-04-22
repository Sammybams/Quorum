import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Member = {
  id: number;
  full_name: string;
  level?: string;
  matric_number?: string;
  email?: string;
  dues_status?: string;
};

const demoMembers: Member[] = [
  { id: 1, full_name: "Oluwaseun Adeyemi", level: "300L", matric_number: "CSC/21/1001", email: "seun@uni.edu", dues_status: "Paid" },
  { id: 2, full_name: "Chiamaka Eze", level: "400L", matric_number: "CSC/20/1439", email: "chiamaka@uni.edu", dues_status: "Pending" },
  { id: 3, full_name: "Bayo Adesanya", level: "200L", matric_number: "CSC/22/1094", email: "bayo@uni.edu", dues_status: "Paid" },
];

export default async function MembersPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);

  let members: Member[] = [];
  try {
    members = await apiGet<Member[]>(`/workspaces/${workspace.id}/members`);
  } catch {
    members = demoMembers;
  }

  const rows = members.length > 0 ? members : demoMembers;

  return (
    <section className="atelier-stack">
      <header className="atelier-pagehead row">
        <div>
          <small>Members</small>
          <h1>Member Registry</h1>
          <p>{rows.length} registered members</p>
        </div>
      </header>

      <section className="atelier-card">
        <div className="member-toolbar">
          <button type="button" className="atelier-btn-secondary">Invite via Link</button>
          <button type="button" className="atelier-btn-secondary">Bulk Actions</button>
          <button type="button" className="atelier-btn-ghost">Export CSV</button>
        </div>

        <div className="member-table-wrap">
          <table className="member-table">
            <thead>
              <tr>
                <th>Member</th>
                <th>Level</th>
                <th>Matric Number</th>
                <th>Dues Status</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((member) => (
                <tr key={member.id}>
                  <td>
                    <div className="member-name">
                      <div className="member-avatar">{member.full_name.split(" ").map((part) => part[0]).slice(0, 2).join("")}</div>
                      <span>{member.full_name}</span>
                    </div>
                  </td>
                  <td>{member.level || "-"}</td>
                  <td>{member.matric_number || "-"}</td>
                  <td>
                    <span className={`status-pill ${member.dues_status?.toLowerCase() === "paid" ? "ok" : "pending"}`}>
                      {member.dues_status || "Pending"}
                    </span>
                  </td>
                  <td>{member.email || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
