// src/routes/api.mjs
import express from 'express';  // Use ESM import for express
import { getUrls } from '../controllers/apiController.mjs';  // Import getUrls from the controller
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { dirname } from 'path';
import { fileURLToPath } from 'url';

const router = express.Router();

router.get('/urls', getUrls);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const publicDirectory = path.join(__dirname, '../../public');

// Route to trigger the Python script
router.post('/generate-map', (req, res) => {

    console.log('Request Body:', req.body);

    const {states, years, resolution} = req.body;

    if (!states || !years || !resolution) {
      return res.status(400).json({ 
          error: 'Missing required parameters',
          details: { states, years, resolution }
      });
  }
    const pythonProcess = spawn('python', [
      path.join(__dirname, '..', 'python-scripts', 'mapGenerator.py'),
      resolution,
      years.join(','),
      states.join(','),
    ]);
  
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      try {
        const outputObject = JSON.parse(output);
        const htmlFilePath = outputObject.map_html_path;
        
        const filename = path.basename(htmlFilePath);   
        const publicHtmlFilePath = path.join(publicDirectory, 'maps', filename); 

        fs.mkdirSync(path.dirname(publicHtmlFilePath), { recursive: true });
        fs.copyFileSync(htmlFilePath, publicHtmlFilePath);
        fs.unlinkSync(htmlFilePath);
    
        res.status(200).json({ success: true, htmlFilePath: `/maps/${filename}` });
  
      } catch (error) {
        console.error('Error parsing Python script output:', error);
        res.status(500).json({ error: 'Failed to generate map' });
      }
    });
  
    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python Error: ${data}`);
      res.status(500).json({ error: 'An error occurred while generating the map.' });
    });
  
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        res.status(500).json({ error: `Python process exited with code ${code}` });
      }
    });
  });

export default router;