import express from 'express';
import apiRoutes from './routes/api.mjs';
import logger from './middlewares/logger.mjs';
import dotenv from 'dotenv'; 

dotenv.config();

const app = express();
const port = 5000;

app.use(express.json()); 

app.use(express.static('public'));

// Use the API routes
app.use('/api', apiRoutes);

app.get('/', (req, res) => {
  res.sendFile('index.html', { root: 'public' });
});

app.use(logger)

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});