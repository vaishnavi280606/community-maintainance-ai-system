import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Typography, Box, Divider, Avatar, Chip, Dialog,
  DialogContent, DialogActions, Button, TextField, Switch,
  FormControlLabel, Alert, Badge, IconButton,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Report as ReportIcon,
  Notifications as NotifIcon,
  Logout as LogoutIcon,
  Build as BuildIcon,
  Engineering as TechIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { useAuth } from '../AuthContext';
import { getProfile, updateProfile, getNotifications } from '../api';

const DRAWER_WIDTH = 250;

const menuItems = {
  admin: [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Complaints', icon: <ReportIcon />, path: '/complaints' },
    { text: 'Technicians', icon: <TechIcon />, path: '/technicians' },
    { text: 'Notifications', icon: <NotifIcon />, path: '/notifications', badge: true },
  ],
  resident: [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'My Complaints', icon: <ReportIcon />, path: '/complaints' },
    { text: 'Notifications', icon: <NotifIcon />, path: '/notifications', badge: true },
  ],
  technician: [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'My Tasks', icon: <ReportIcon />, path: '/complaints' },
    { text: 'Notifications', icon: <NotifIcon />, path: '/notifications', badge: true },
  ],
};

const ROLE_COLORS = { admin: '#ff1744', resident: '#00bfa5', technician: '#ff9100' };
const ROLE_LABELS = { admin: 'Administrator', resident: 'Resident', technician: 'Technician' };

export default function Sidebar() {
  const { user, logout, loginUser, tokens } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const role = user?.role || 'resident';
  const items = menuItems[role] || menuItems.resident;

  // Profile dialog state
  const [profileOpen, setProfileOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);

  // Fetch unread notifications count
  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const res = await getNotifications(true);
        setUnreadCount(res.data.unread_count || 0);
      } catch (e) { /* ignore */ }
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);

  const openProfile = async () => {
    try {
      const res = await getProfile();
      setProfileData(res.data);
      setForm(res.data);
    } catch (e) {
      setProfileData(user);
      setForm(user || {});
    }
    setEditing(false);
    setSuccess('');
    setError('');
    setProfileOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const res = await updateProfile(form);
      setProfileData(res.data);
      loginUser(res.data, tokens);
      setEditing(false);
      setSuccess('Profile updated!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (e) {
      setError('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const displayName = user?.first_name
    ? `${user.first_name} ${user.last_name || ''}`.trim()
    : user?.username || 'User';

  return (
    <>
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH, boxSizing: 'border-box',
            background: 'linear-gradient(195deg, #0a1128 0%, #1a237e 50%, #283593 100%)',
            color: '#fff', border: 'none',
            overflowX: 'hidden',
          },
        }}
      >
        {/* Brand */}
        <Box sx={{ pt: 2.5, pb: 1.5, textAlign: 'center' }}>
          <Box sx={{
            width: 44, height: 44, borderRadius: 2.5, mx: 'auto', mb: 0.8,
            background: 'linear-gradient(135deg, #00bfa5 0%, #1de9b6 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 20px rgba(0,191,165,0.35)',
          }}>
            <Typography variant="h6" fontWeight={900} sx={{ color: '#fff' }}>C</Typography>
          </Box>
          <Typography variant="body1" fontWeight={800} sx={{ color: '#fff', letterSpacing: '0.06em', fontSize: 15 }}>
            CMS AI
          </Typography>
          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)', fontSize: 10, display: 'block' }}>
            Community Maintenance
          </Typography>
        </Box>

        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.06)', mx: 2, mb: 0.5 }} />

        {/* User Info — clickable */}
        <Box
          onClick={openProfile}
          sx={{
            px: 2, py: 1.5, mx: 1, my: 0.5, borderRadius: 2,
            display: 'flex', alignItems: 'center', gap: 1.2,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            '&:hover': { bgcolor: 'rgba(255,255,255,0.08)' },
          }}
        >
          <Avatar sx={{
            width: 36, height: 36, fontSize: 14, fontWeight: 700,
            background: `linear-gradient(135deg, ${ROLE_COLORS[role]}, ${ROLE_COLORS[role]}cc)`,
            boxShadow: `0 2px 8px ${ROLE_COLORS[role]}44`,
          }}>
            {(user?.first_name?.[0] || user?.username?.[0] || '?').toUpperCase()}
          </Avatar>
          <Box sx={{ overflow: 'hidden', flex: 1 }}>
            <Typography variant="body2" fontWeight={700} sx={{ color: '#fff', fontSize: 13 }} noWrap>
              {displayName}
            </Typography>
            <Chip label={ROLE_LABELS[role]} size="small" sx={{
              height: 18, fontSize: 9, fontWeight: 700,
              bgcolor: `${ROLE_COLORS[role]}20`, color: ROLE_COLORS[role],
              border: `1px solid ${ROLE_COLORS[role]}33`,
              mt: 0.2,
            }} />
          </Box>
        </Box>

        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.06)', mx: 2, mt: 0.5 }} />

        {/* Menu */}
        <List sx={{ flex: 1, px: 1, py: 1.5 }}>
          {items.map((item) => {
            const isActive = location.pathname === item.path;
            const icon = item.badge && unreadCount > 0
              ? <Badge badgeContent={unreadCount} color="error" sx={{ '& .MuiBadge-badge': { fontSize: 10, height: 18, minWidth: 18 } }}>{item.icon}</Badge>
              : item.icon;
            return (
              <ListItemButton
                key={item.text}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2, mb: 0.3, py: 1, px: 1.5,
                  bgcolor: isActive ? 'rgba(0,191,165,0.12)' : 'transparent',
                  borderLeft: isActive ? '3px solid #00bfa5' : '3px solid transparent',
                  '&:hover': { bgcolor: isActive ? 'rgba(0,191,165,0.18)' : 'rgba(255,255,255,0.06)' },
                  transition: 'all 0.2s ease',
                }}
              >
                <ListItemIcon sx={{
                  color: isActive ? '#00bfa5' : 'rgba(255,255,255,0.5)',
                  minWidth: 34, fontSize: 20,
                }}>
                  {icon}
                </ListItemIcon>
                <ListItemText primary={item.text} primaryTypographyProps={{
                  fontWeight: isActive ? 700 : 500,
                  fontSize: 13,
                  color: isActive ? '#fff' : 'rgba(255,255,255,0.7)',
                }} />
                {isActive && (
                  <Box sx={{
                    width: 5, height: 5, borderRadius: '50%', bgcolor: '#00bfa5',
                    boxShadow: '0 0 8px #00bfa5',
                  }} />
                )}
              </ListItemButton>
            );
          })}
        </List>

        {/* Technician availability quick toggle */}
        {user?.role === 'technician' && (
          <>
            <Divider sx={{ bgcolor: 'rgba(255,255,255,0.06)', mx: 2 }} />
            <Box sx={{ px: 2, py: 1.5 }}>
              <FormControlLabel
                control={
                  <Switch
                    size="small"
                    checked={user?.is_available ?? true}
                    onChange={async (e) => {
                      try {
                        const res = await updateProfile({ is_available: e.target.checked });
                        loginUser(res.data, tokens);
                      } catch (err) { console.error(err); }
                    }}
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': { color: '#00bfa5' },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#00bfa5' },
                    }}
                  />
                }
                label={
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: 11 }}>
                    {user?.is_available ? 'Available' : 'Unavailable'}
                  </Typography>
                }
              />
            </Box>
          </>
        )}

        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.06)', mx: 2 }} />
        <ListItemButton onClick={logout} sx={{
          mx: 1, mb: 1.5, mt: 0.5, borderRadius: 2, py: 1,
          '&:hover': { bgcolor: 'rgba(255,23,68,0.12)' },
        }}>
          <ListItemIcon sx={{ color: 'rgba(255,255,255,0.5)', minWidth: 34 }}><LogoutIcon fontSize="small" /></ListItemIcon>
          <ListItemText primary="Logout" primaryTypographyProps={{
            fontWeight: 500, fontSize: 13, color: 'rgba(255,255,255,0.7)',
          }} />
        </ListItemButton>
      </Drawer>

      {/* ─── Profile Dialog ─── */}
      <Dialog open={profileOpen} onClose={() => setProfileOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3, overflow: 'hidden' } }}>
        {/* Header */}
        <Box sx={{
          background: 'linear-gradient(135deg, #0a1128 0%, #1a237e 50%, #283593 100%)',
          px: 3, pt: 3, pb: 4, position: 'relative',
        }}>
          <IconButton onClick={() => setProfileOpen(false)} sx={{
            position: 'absolute', top: 8, right: 8, color: 'rgba(255,255,255,0.7)',
          }}>
            <CloseIcon fontSize="small" />
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{
              width: 56, height: 56, fontSize: 22, fontWeight: 800,
              background: `linear-gradient(135deg, ${ROLE_COLORS[role]}, ${ROLE_COLORS[role]}aa)`,
              boxShadow: `0 4px 16px ${ROLE_COLORS[role]}55`,
              border: '3px solid rgba(255,255,255,0.2)',
            }}>
              {(profileData?.first_name?.[0] || profileData?.username?.[0] || '?').toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={700} sx={{ color: '#fff', lineHeight: 1.2 }}>
                {profileData?.first_name} {profileData?.last_name}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                @{profileData?.username}
              </Typography>
              <Chip label={ROLE_LABELS[role]} size="small" sx={{
                height: 20, fontSize: 10, fontWeight: 700, mt: 0.5,
                bgcolor: `${ROLE_COLORS[role]}30`, color: '#fff',
                border: `1px solid ${ROLE_COLORS[role]}55`,
              }} />
            </Box>
          </Box>
        </Box>

        <DialogContent sx={{ pt: 2.5, pb: 1 }}>
          {success && <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>{success}</Alert>}
          {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}

          {!editing ? (
            /* View Mode */
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <InfoRow icon={<EmailIcon fontSize="small" />} label="Email" value={profileData?.email || '—'} />
              <InfoRow icon={<PhoneIcon fontSize="small" />} label="Phone" value={profileData?.phone || '—'} />
              <InfoRow icon={<LocationIcon fontSize="small" />} label="Block" value={profileData?.block || '—'} />
              {profileData?.flat_number && (
                <InfoRow icon={<LocationIcon fontSize="small" />} label="Flat" value={profileData.flat_number} />
              )}
              {role === 'technician' && (
                <>
                  <InfoRow icon={<BuildIcon fontSize="small" />} label="Specialization" value={profileData?.specialization || '—'} />
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, py: 0.3 }}>
                    <ShieldIcon fontSize="small" sx={{ color: '#999' }} />
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1 }}>Availability</Typography>
                      <Chip
                        label={profileData?.is_available ? 'Available' : 'Unavailable'}
                        size="small"
                        sx={{
                          mt: 0.3, height: 22, fontWeight: 600,
                          bgcolor: profileData?.is_available ? '#e8f5e9' : '#ffebee',
                          color: profileData?.is_available ? '#2e7d32' : '#c62828',
                        }}
                      />
                    </Box>
                  </Box>
                </>
              )}
            </Box>
          ) : (
            /* Edit Mode */
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField label="First Name" size="small" fullWidth value={form.first_name || ''}
                  onChange={e => setForm({ ...form, first_name: e.target.value })} />
                <TextField label="Last Name" size="small" fullWidth value={form.last_name || ''}
                  onChange={e => setForm({ ...form, last_name: e.target.value })} />
              </Box>
              <TextField label="Email" size="small" fullWidth value={form.email || ''}
                onChange={e => setForm({ ...form, email: e.target.value })} />
              <TextField label="Phone" size="small" fullWidth value={form.phone || ''}
                onChange={e => setForm({ ...form, phone: e.target.value })} />
              <TextField label="Block" size="small" fullWidth value={form.block || ''}
                onChange={e => setForm({ ...form, block: e.target.value })} />
              {role === 'resident' && (
                <TextField label="Flat Number" size="small" fullWidth value={form.flat_number || ''}
                  onChange={e => setForm({ ...form, flat_number: e.target.value })} />
              )}
              {role === 'technician' && (
                <>
                  <TextField label="Specialization" size="small" fullWidth value={form.specialization || ''}
                    onChange={e => setForm({ ...form, specialization: e.target.value })} />
                  <FormControlLabel
                    control={
                      <Switch checked={form.is_available ?? true}
                        onChange={e => setForm({ ...form, is_available: e.target.checked })}
                        sx={{
                          '& .MuiSwitch-switchBase.Mui-checked': { color: '#00bfa5' },
                          '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#00bfa5' },
                        }}
                      />
                    }
                    label="Available for assignments"
                  />
                </>
              )}
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          {!editing ? (
            <Button startIcon={<EditIcon />} onClick={() => setEditing(true)}
              sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600, color: '#1a237e' }}>
              Edit Profile
            </Button>
          ) : (
            <>
              <Button onClick={() => { setEditing(false); setForm(profileData); }}
                sx={{ borderRadius: 2, textTransform: 'none' }}>Cancel</Button>
              <Button variant="contained" onClick={handleSave} disabled={saving}
                sx={{
                  borderRadius: 2, textTransform: 'none', fontWeight: 600,
                  background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
                }}>
                Save Changes
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}

/* Helper component for profile info rows */
function InfoRow({ icon, label, value }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, py: 0.3 }}>
      <Box sx={{ color: '#999' }}>{icon}</Box>
      <Box>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1 }}>{label}</Typography>
        <Typography variant="body2" fontWeight={500}>{value}</Typography>
      </Box>
    </Box>
  );
}

export { DRAWER_WIDTH };
