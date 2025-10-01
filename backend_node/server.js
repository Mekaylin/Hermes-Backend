/* Entry point for Hermes Node backend
   - Loads env
   - Configures routes
*/

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const port = process.env.PORT || 8080;

// Routes
const marketRoutes = require('./routes/marketRoutes');
const indicatorRoutes = require('./routes/indicatorRoutes');
const newsRoutes = require('./routes/newsRoutes');
const aiRoutes = require('./routes/aiRoutes');

app.use('/market-data', marketRoutes);
app.use('/indicators', indicatorRoutes);
app.use('/news-sentiment', newsRoutes);
app.use('/ai-input', aiRoutes);

app.get('/', (req, res) => res.json({ message: 'Hermes Node backend running' }));

if (require.main === module) {
   app.listen(port, () => console.log(`Hermes backend listening on ${port}`));
}

module.exports = app;
