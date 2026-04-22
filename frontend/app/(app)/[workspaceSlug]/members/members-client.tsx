"use client";

import { FormEvent, useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Member = {
  id: number;
  workspace_id?: number;
  full_name: string;
  level?: string | null;
  email?: string | null;
  role: string;
  dues_status?: string;
};

export default function MembersClient({
  workspace,
  initialMembers,
}: {
  workspace: Workspace;
  initialMembers: Member[];
}) {
  const [members, setMembers] = useState(initialMembers);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [level, setLevel] = useState("");
  const [role, setRole] = useState("member");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const inviteUrl = useMemo(() => {
    if (typeof window === "undefined") {
      return `/portal/${workspace.slug}`;
    }
    return `${window.location.origin}/portal/${workspace.slug}`;
  }, [workspace.slug]);

  async function copyInviteLink() {
    await navigator.clipboard.writeText(inviteUrl);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const member = await apiPost<
        Member,
        { full_name: string; email: string; role: string; level?: string }
      >(`/workspaces/${workspace.id}/members`, {
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        role,
        level: level.trim() || undefined,
      });

      setMembers((current) => [member, ...current]);
      setFullName("");
      setEmail("");
      setLevel("");
      setRole("member");
      setInviteOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to invite member.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Members</p>
          <h1>Member registry</h1>
          <p>
            {members.length} registered {members.length === 1 ? "member" : "members"}
          </p>
        </div>
        <div className="page-actions">
          <button type="button" className="btn-secondary" onClick={() => setInviteOpen(true)}>
            <span className="material-symbols-outlined" aria-hidden="true">
              person_add
            </span>
            Invite
          </button>
          <button type="button" className="btn-ghost">
            Export CSV
          </button>
        </div>
      </header>

      <section className="panel-card">
        {members.length === 0 ? (
          <div className="empty-state">
            <span className="material-symbols-outlined" aria-hidden="true">
              group
            </span>
            <h2>No members yet</h2>
            <p>Add a member directly or copy the portal link for your workspace.</p>
            <button type="button" className="btn-primary" onClick={() => setInviteOpen(true)}>
              Invite first member
            </button>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Level</th>
                  <th>Role</th>
                  <th>Dues</th>
                  <th>Email</th>
                </tr>
              </thead>
              <tbody>
                {members.map((member) => (
                  <tr key={member.id}>
                    <td>
                      <div className="member-name">
                        <span className="member-avatar">{initials(member.full_name)}</span>
                        <strong>{member.full_name}</strong>
                      </div>
                    </td>
                    <td>{member.level || "-"}</td>
                    <td>{member.role}</td>
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
        )}
      </section>

      {inviteOpen ? (
        <div className="modal-backdrop" role="presentation" onClick={() => setInviteOpen(false)}>
          <section
            className="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="invite-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="card-head compact">
              <div>
                <p className="eyebrow">Invite</p>
                <h2 id="invite-title">Add a member</h2>
              </div>
              <button type="button" className="icon-button" aria-label="Close invite modal" onClick={() => setInviteOpen(false)}>
                <span className="material-symbols-outlined" aria-hidden="true">
                  close
                </span>
              </button>
            </div>

            <div className="invite-link-box">
              <span>{inviteUrl}</span>
              <button type="button" className="btn-secondary" onClick={copyInviteLink}>
                {copied ? "Copied" : "Copy link"}
              </button>
            </div>

            <form className="form-stack" onSubmit={onSubmit}>
              <label>
                Full name
                <input
                  type="text"
                  placeholder="Jane Doe"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  required
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  placeholder="jane@school.edu.ng"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </label>
              <div className="form-two">
                <label>
                  Level
                  <input
                    type="text"
                    placeholder="300L"
                    value={level}
                    onChange={(event) => setLevel(event.target.value)}
                  />
                </label>
                <label>
                  Role
                  <select value={role} onChange={(event) => setRole(event.target.value)}>
                    <option value="member">Member</option>
                    <option value="exco">Exco officer</option>
                    <option value="secretary">Secretary</option>
                    <option value="treasurer">Treasurer</option>
                  </select>
                </label>
              </div>

              {error ? <p className="form-error">{error}</p> : null}

              <div className="form-actions">
                <button type="button" className="btn-ghost" onClick={() => setInviteOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? "Adding..." : "Add member"}
                </button>
              </div>
            </form>
          </section>
        </div>
      ) : null}
    </section>
  );
}

function initials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}
