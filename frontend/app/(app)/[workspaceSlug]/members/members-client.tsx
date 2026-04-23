"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { apiGet, apiPost } from "@/lib/api";

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
type Role = { id: number; name: string; key: string; is_system_role: boolean };
type Invitation = { id: number; email: string; role_name: string; token: string; status: string };
type InviteLink = { id: number; token: string; role_name: string; is_active: boolean };

export default function MembersClient({
  workspace,
  initialMembers,
}: {
  workspace: Workspace;
  initialMembers: Member[];
}) {
  const [members, setMembers] = useState(initialMembers);
  const [roles, setRoles] = useState<Role[]>([]);
  const [pendingInvitations, setPendingInvitations] = useState<Invitation[]>([]);
  const [inviteLinks, setInviteLinks] = useState<InviteLink[]>([]);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [roleId, setRoleId] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function loadInviteData() {
      try {
        const [loadedRoles, loadedInvitations, loadedInviteLinks] = await Promise.all([
          apiGet<Role[]>(`/workspaces/${workspace.id}/roles`),
          apiGet<Invitation[]>(`/workspaces/${workspace.id}/invitations`),
          apiGet<InviteLink[]>(`/workspaces/${workspace.id}/invite-links`),
        ]);
        setRoles(loadedRoles);
        setPendingInvitations(loadedInvitations);
        setInviteLinks(loadedInviteLinks);
        const coreRole = loadedRoles.find((item) => item.key === "core_member") || loadedRoles[0] || null;
        setRoleId(coreRole?.id || null);
      } catch {
        // Role/invite loading requires a logged-in admin token; the page itself can still render read-only.
      }
    }

    loadInviteData();
  }, [workspace.id]);

  const inviteUrl = useMemo(() => {
    const token = inviteLinks.find((link) => link.is_active)?.token;
    if (!token) {
      return null;
    }
    if (typeof window === "undefined") {
      return `/join/${token}`;
    }
    return `${window.location.origin}/join/${token}`;
  }, [inviteLinks]);

  async function copyInviteLink() {
    if (!inviteUrl) {
      setError("Generate a bulk invite link before copying.");
      return;
    }
    await navigator.clipboard.writeText(inviteUrl);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  async function createInviteLink() {
    if (!roleId) {
      setError("Select a role before creating an invite link.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const link = await apiPost<InviteLink, { role_id: number }>(`/workspaces/${workspace.id}/invite-links`, {
        role_id: roleId,
      });
      setInviteLinks((current) => [link, ...current]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create invite link.");
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!roleId) {
      setError("Select a role before sending an invitation.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const invitation = await apiPost<Invitation, { email: string; role_id: number; note?: string }>(
        `/workspaces/${workspace.id}/invitations`,
        {
          email: email.trim().toLowerCase(),
          role_id: roleId,
          note: note.trim() || undefined,
        },
      );

      setPendingInvitations((current) => [invitation, ...current]);
      setEmail("");
      setNote("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to send invitation.");
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
            <p>Send an email invitation or create a bulk invite link for your workspace.</p>
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
                <h2 id="invite-title">Invite members</h2>
              </div>
              <button type="button" className="icon-button" aria-label="Close invite modal" onClick={() => setInviteOpen(false)}>
                <span className="material-symbols-outlined" aria-hidden="true">
                  close
                </span>
              </button>
            </div>

            <div className="invite-link-box">
              <span>{inviteUrl || "No bulk invite link yet. Generate one to copy a /join link."}</span>
              <button type="button" className="btn-secondary" onClick={copyInviteLink} disabled={!inviteUrl}>
                {copied ? "Copied" : "Copy link"}
              </button>
            </div>
            <button type="button" className="btn-primary" onClick={createInviteLink} disabled={loading || !roleId}>
              {inviteUrl ? "Generate another invite link" : "Generate bulk invite link"}
            </button>

            <form className="form-stack" onSubmit={onSubmit}>
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
              <label>
                Role
                <select value={roleId || ""} onChange={(event) => setRoleId(Number(event.target.value))}>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Personal note
                <textarea
                  rows={3}
                  placeholder="Optional message shown in the invitation email"
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                />
              </label>

              {error ? <p className="form-error">{error}</p> : null}

              {pendingInvitations.length > 0 ? (
                <div className="mini-list">
                  {pendingInvitations.slice(0, 4).map((invitation) => (
                    <div key={invitation.id}>
                      <span>{invitation.email}</span>
                      <strong>{invitation.role_name} · {invitation.status}</strong>
                    </div>
                  ))}
                </div>
              ) : null}

              <div className="form-actions">
                <button type="button" className="btn-ghost" onClick={() => setInviteOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? "Sending..." : "Send invitation"}
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
