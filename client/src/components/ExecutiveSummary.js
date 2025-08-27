import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Stack,
  Chip,
  Button,
  Paper,
  useTheme,
  Divider
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Public,
  HealthAndSafety,
  Savings,
  Speed,
  Security,
  EmojiObjects,
  BusinessCenter,
  Timeline,
  Group
} from '@mui/icons-material';

const ExecutiveSummary = () => {
  const theme = useTheme();

  const ProblemCard = ({ icon, title, stat, description, color }) => (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.03 }}
    >
      <Card 
        elevation={4}
        sx={{ 
          height: '100%',
          background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
          border: `2px solid ${color}30`,
          borderRadius: 3
        }}
      >
        <CardContent sx={{ textAlign: 'center', p: 3 }}>
          <Avatar sx={{ bgcolor: color, width: 64, height: 64, mx: 'auto', mb: 2 }}>
            {icon}
          </Avatar>
          <Typography variant="h3" sx={{ fontWeight: 'bold', color, mb: 1 }}>
            {stat}
          </Typography>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            {title}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {description}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );

  const SolutionFeature = ({ icon, title, description, color }) => (
    <motion.div
      initial={{ x: -30, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
        <Avatar sx={{ bgcolor: color, mr: 2, mt: 0.5 }}>
          {icon}
        </Avatar>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
            {title}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {description}
          </Typography>
        </Box>
      </Box>
    </motion.div>
  );

  const BusinessModelCard = ({ title, description, revenue, examples, color }) => (
    <Card elevation={3} sx={{ height: '100%', border: `2px solid ${color}20` }}>
      <CardContent>
        <Typography variant="h6" sx={{ color, fontWeight: 600, mb: 2 }}>
          {title}
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          {description}
        </Typography>
        <Chip 
          label={revenue} 
          color="primary" 
          variant="outlined" 
          size="small" 
          sx={{ mb: 2 }} 
        />
        <Typography variant="caption" color="textSecondary">
          {examples}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      {/* Header */}
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <Paper
          elevation={6}
          sx={{
            background: `linear-gradient(135deg, ${theme.palette.primary.main}15 0%, ${theme.palette.secondary.main}10 100%)`,
            p: 4,
            mb: 4,
            textAlign: 'center',
            borderRadius: 4
          }}
        >
          <Typography 
            variant="h2" 
            sx={{ 
              fontWeight: 'bold', 
              mb: 2, 
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            🩺 Vital Trace
          </Typography>
          <Typography variant="h5" color="textSecondary" sx={{ mb: 3, fontStyle: 'italic' }}>
            Ensuring the Last Mile of Healthcare
          </Typography>
          <Typography variant="h6" color="textSecondary" sx={{ mb: 4 }}>
            IoT-powered cold chain monitoring system preventing vaccine wastage and saving lives
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Chip label="Healthcare Technology" color="primary" />
            <Chip label="IoT Solutions" color="secondary" />
            <Chip label="Global Impact" color="success" />
            <Chip label="WHO Compliant" color="warning" />
          </Stack>
        </Paper>
      </motion.div>

      {/* The Problem */}
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
        🚨 The Global Healthcare Crisis
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 4, textAlign: 'center', maxWidth: 800, mx: 'auto' }}>
        The "last mile" of healthcare delivery faces critical challenges, especially in remote and rural areas. 
        Cold chain failures result in massive vaccine wastage, preventing life-saving immunizations and eroding public trust.
      </Typography>

      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={3}>
          <ProblemCard
            icon={<HealthAndSafety fontSize="large" />}
            title="Vaccine Wastage"
            stat="50%"
            description="of vaccines are wasted globally every year due to cold chain failures"
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <ProblemCard
            icon={<Savings fontSize="large" />}
            title="Economic Loss"
            stat="$5B+"
            description="in annual losses from vaccine wastage and logistics failures"
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <ProblemCard
            icon={<Public fontSize="large" />}
            title="Lives at Risk"
            stat="1.5M"
            description="preventable deaths annually due to vaccine access failures"
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <ProblemCard
            icon={<Timeline fontSize="large" />}
            title="Trust Erosion"
            stat="73%"
            description="of rural communities lose confidence after vaccine program failures"
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* The Solution */}
      <Divider sx={{ my: 6 }} />
      
      <Grid container spacing={6} alignItems="center">
        <Grid item xs={12} md={6}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 3 }}>
            💡 Our Solution: Vital Trace Ecosystem
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
            Vital Trace is not just a smart cooler—it's an end-to-end IoT ecosystem consisting of 
            the physical Vital Trace Box, cloud backend, and web dashboard, providing complete cold chain visibility.
          </Typography>

          <SolutionFeature
            icon={<Speed />}
            title="Real-time Monitoring"
            description="Continuous temperature, GPS, and tamper detection with instant alerts"
            color="#2e7d32"
          />
          
          <SolutionFeature
            icon={<EmojiObjects />}
            title="Smart Active Cooling"
            description="AI-controlled Peltier cooling system maintains 2-8°C range automatically"
            color="#1976d2"
          />
          
          <SolutionFeature
            icon={<Public />}
            title="Solar-Powered Sustainability"
            description="Off-grid operation with solar charging for remote area deployment"
            color="#ed6c02"
          />
          
          <SolutionFeature
            icon={<Security />}
            title="Complete Audit Trail"
            description="100% regulatory compliance with WHO and national health standards"
            color="#9c27b0"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <Paper
              elevation={8}
              sx={{
                p: 4,
                textAlign: 'center',
                background: `linear-gradient(135deg, ${theme.palette.primary.main}10 0%, ${theme.palette.secondary.main}05 100%)`,
                borderRadius: 4
              }}
            >
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, color: 'primary.main' }}>
                🎯 Impact Delivered
              </Typography>
              
              <Stack spacing={3}>
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
                    90%+
                  </Typography>
                  <Typography variant="body1" color="textSecondary">
                    Reduction in vaccine wastage
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
                    25+
                  </Typography>
                  <Typography variant="body1" color="textSecondary">
                    Active deployment locations
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#ed6c02' }}>
                    100%
                  </Typography>
                  <Typography variant="body1" color="textSecondary">
                    Regulatory compliance achieved
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* Business Model */}
      <Divider sx={{ my: 6 }} />
      
      <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
        💼 Business Model & Revenue Streams
      </Typography>
      
      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={4}>
          <BusinessModelCard
            title="Hardware + SaaS"
            description="Sell Vital Trace boxes with monthly cloud platform subscription"
            revenue="$2,000/box + $50/month/box"
            examples="Primary revenue model for government health departments"
            color="#2e7d32"
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <BusinessModelCard
            title="Service Lease Model"
            description="Lease boxes with full-service maintenance and support included"
            revenue="$200/month/box all-inclusive"
            examples="Ideal for NGOs and international health organizations"
            color="#1976d2"
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <BusinessModelCard
            title="Enterprise Licensing"
            description="White-label platform licensing for pharmaceutical companies"
            revenue="$100K+ annual licenses"
            examples="Vaccine manufacturers, cold chain logistics companies"
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Market Opportunity */}
      <Paper elevation={4} sx={{ p: 4, mb: 4, background: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50' }}>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
          📈 Market Opportunity
        </Typography>
        
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                $12.9B
              </Typography>
              <Typography variant="h6" color="textSecondary">
                Global Cold Chain Market (2024)
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'secondary.main' }}>
                15.4%
              </Typography>
              <Typography variant="h6" color="textSecondary">
                Expected Annual Growth (CAGR)
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                $21.2B
              </Typography>
              <Typography variant="h6" color="textSecondary">
                Projected Market Size (2030)
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Call to Action */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <Paper
          elevation={8}
          sx={{
            p: 4,
            textAlign: 'center',
            background: `linear-gradient(135deg, ${theme.palette.primary.main}20 0%, ${theme.palette.secondary.main}15 100%)`,
            borderRadius: 4
          }}
        >
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 2 }}>
            🚀 Ready to Transform Healthcare?
          </Typography>
          <Typography variant="h6" color="textSecondary" sx={{ mb: 3 }}>
            Join us in ensuring the last mile of healthcare reaches everyone, everywhere.
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button 
              variant="contained" 
              size="large" 
              startIcon={<BusinessCenter />}
              sx={{ borderRadius: 3 }}
            >
              Schedule Demo
            </Button>
            <Button 
              variant="outlined" 
              size="large" 
              startIcon={<Group />}
              sx={{ borderRadius: 3 }}
            >
              Partner With Us
            </Button>
          </Stack>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default ExecutiveSummary;
