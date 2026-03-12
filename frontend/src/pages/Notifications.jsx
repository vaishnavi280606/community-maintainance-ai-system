import { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, List, ListItem, ListItemText, ListItemIcon,
  IconButton, Button, Chip, CircularProgress, Divider,
} from '@mui/material';
import {
  Notifications as NotifIcon,
  MarkEmailRead as ReadIcon,
  Circle as UnreadIcon,
  Assignment as AssignIcon,
  Update as UpdateIcon,
  CheckCircle as ResolveIcon,
  Warning as AlertIcon,
  ContentCopy as DupIcon,
  Build as MaintIcon,
} from '@mui/icons-material';
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '../api';

const TYPE_CONFIG = {
  complaint_assigned: { color: '#1a237e', icon: <AssignIcon fontSize="small" /> },
  complaint_updated: { color: '#0288d1', icon: <UpdateIcon fontSize="small" /> },
  complaint_resolved: { color: '#2e7d32', icon: <ResolveIcon fontSize="small" /> },
  maintenance_alert: { color: '#e65100', icon: <MaintIcon fontSize="small" /> },
  duplicate_detected: { color: '#7b1fa2', icon: <DupIcon fontSize="small" /> },
  root_cause_alert: { color: '#c62828', icon: <AlertIcon fontSize="small" /> },
};

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const loadNotifications = async () => {
    try {
      const res = await getNotifications();
      setNotifications(res.data.notifications);
      setUnreadCount(res.data.unread_count);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadNotifications(); }, []);

  const handleMarkRead = async (id) => {
    await markNotificationRead(id);
    loadNotifications();
  };

  const handleMarkAllRead = async () => {
    await markAllNotificationsRead();
    loadNotifications();
  };

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <CircularProgress size={48} sx={{ color: '#1a237e' }} />
    </Box>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{
            background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            Notifications
            {unreadCount > 0 && (
              <Chip label={unreadCount} size="small" sx={{
                ml: 1.5, fontWeight: 800, bgcolor: '#ff1744', color: '#fff',
                height: 24, minWidth: 24,
              }} />
            )}
          </Typography>
          <Typography variant="body2" color="text.secondary">Stay updated on your complaints and tasks</Typography>
        </Box>
        {unreadCount > 0 && (
          <Button variant="outlined" startIcon={<ReadIcon />} onClick={handleMarkAllRead} sx={{
            borderRadius: 3, fontWeight: 600, borderColor: '#1a237e', color: '#1a237e',
            '&:hover': { bgcolor: '#e8eaf6', borderColor: '#1a237e' },
          }}>
            Mark All Read
          </Button>
        )}
      </Box>

      <Paper sx={{ borderRadius: 4, overflow: 'hidden' }}>
        <List disablePadding>
          {notifications.length === 0 ? (
            <ListItem sx={{ py: 6 }}>
              <ListItemText
                primary={<Typography variant="h6" textAlign="center" color="text.secondary">All caught up!</Typography>}
                secondary={<Typography variant="body2" textAlign="center" color="text.secondary">No notifications to show</Typography>}
              />
            </ListItem>
          ) : (
            notifications.map((n, i) => {
              const config = TYPE_CONFIG[n.notification_type] || { color: '#666', icon: <NotifIcon fontSize="small" /> };
              return (
                <Box key={n.id}>
                  <ListItem
                    sx={{
                      py: 2, px: 3,
                      bgcolor: n.is_read ? 'transparent' : 'rgba(26,35,126,0.03)',
                      borderLeft: n.is_read ? '4px solid transparent' : `4px solid ${config.color}`,
                      transition: 'all 0.2s ease',
                      '&:hover': { bgcolor: 'rgba(26,35,126,0.04)' },
                    }}
                    secondaryAction={
                      !n.is_read && (
                        <IconButton size="small" onClick={() => handleMarkRead(n.id)}
                          sx={{ color: '#1a237e', '&:hover': { bgcolor: '#e8eaf6' } }}>
                          <ReadIcon fontSize="small" />
                        </IconButton>
                      )
                    }
                  >
                    <ListItemIcon sx={{ minWidth: 44 }}>
                      <Box sx={{
                        width: 36, height: 36, borderRadius: 2,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        bgcolor: `${config.color}14`, color: config.color,
                      }}>
                        {config.icon}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Typography variant="body2" fontWeight={n.is_read ? 500 : 700}>
                            {n.title}
                          </Typography>
                          <Chip label={n.notification_type.replace(/_/g, ' ')}
                            size="small" sx={{
                              height: 20, fontSize: 10, fontWeight: 700,
                              bgcolor: `${config.color}14`, color: config.color,
                            }} />
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>{n.message}</Typography>
                          <Typography variant="caption" color="text.disabled">
                            {new Date(n.created_at).toLocaleString()}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  {i < notifications.length - 1 && <Divider sx={{ mx: 3 }} />}
                </Box>
              );
            })
          )}
        </List>
      </Paper>
    </Box>
  );
}
