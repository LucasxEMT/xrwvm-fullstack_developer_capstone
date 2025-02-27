const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

// Read local JSON data
const reviews_data = JSON.parse(fs.readFileSync("reviews.json", 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync("dealerships.json", 'utf8'));

// Connect to MongoDB (named "dealershipsDB"), via the mongo_db container
mongoose.connect("mongodb://mongo_db:27017/", { dbName: 'dealershipsDB' });

// Mongoose models
const Reviews = require('./review');
const Dealerships = require('./dealership');

// Initialize the DB by removing all docs and re-inserting from JSON
try {
  Reviews.deleteMany({}).then(() => {
    Reviews.insertMany(reviews_data['reviews']);
  });
  Dealerships.deleteMany({}).then(() => {
    Dealerships.insertMany(dealerships_data['dealerships']);
  });
} catch (error) {
  // 'res' is not defined in this scope, so just log error here
  console.error('Error initializing documents:', error);
}

// Root endpoint
app.get('/', async (req, res) => {
  res.send("Welcome to the Mongoose API");
});

// Fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Fetch reviews for a specific dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// =========================
// Fetch ALL dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

// Fetch dealerships by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const stateParam = req.params.state; 
    const documents = await Dealerships.find({ state: stateParam });
    res.json(documents);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

// Fetch a single dealer by ID
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const dealerId = parseInt(req.params.id, 10);
    const document = await Dealerships.findOne({ id: dealerId });
    if (document) {
      res.json(document);
    } else {
      res.status(404).json({ error: 'Dealer not found' });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error fetching dealer by ID' });
  }
});
// =========================

// Insert a new review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  let data;
  try {
    data = JSON.parse(req.body);
  } catch (error) {
    return res.status(400).json({ error: 'Invalid JSON body' });
  }
  
  // Find last inserted review and increment ID
  const documents = await Reviews.find().sort({ id: -1 });
  let new_id = documents[0] ? documents[0].id + 1 : 1;

  const review = new Reviews({
    id: new_id,
    name: data['name'],
    dealership: data['dealership'],
    review: data['review'],
    purchase: data['purchase'],
    purchase_date: data['purchase_date'],
    car_make: data['car_make'],
    car_model: data['car_model'],
    car_year: data['car_year'],
  });

  try {
    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
