/* jshint node: true, esversion: 10, globalstrict: true */
'use strict';

const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

// Load initial JSON data
const reviews_data = JSON.parse(fs.readFileSync('reviews.json', 'utf8'));
const dealerships_data = JSON.parse(
  fs.readFileSync('dealerships.json', 'utf8')
);

// Connect to MongoDB
mongoose.connect('mongodb://mongo_db:27017/', { dbName: 'dealershipsDB' });

// Load Mongoose Models
const Reviews = require('./review');
const Dealerships = require('./dealership');

// Seed data (wrapped in a try/catch to avoid unhandled exceptions)
try {
  // Replace existing data in Reviews collection
  Reviews.deleteMany({}).then(() => {
    Reviews.insertMany(reviews_data.reviews);
  });

  // Replace existing data in Dealerships collection
  Dealerships.deleteMany({}).then(() => {
    Dealerships.insertMany(dealerships_data.dealerships);
  });
} catch (error) {
  console.error('Error seeding data:', error);
}

// Express route to home
app.get('/', async (req, res) => {
  res.send('Welcome to the Mongoose API');
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch dealers by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  const stateParam = req.params.state;
  try {
    const documents = await Dealerships.find({ state: stateParam });
    res.json(documents);
  } catch (error) {
    res
      .status(500)
      .json({ error: 'Error fetching dealerships by state' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const documents = await Dealerships.find({ id: req.params.id });
    res.json(documents);
  } catch (error) {
    res
      .status(500)
      .json({ error: 'Error fetching dealerships by ID' });
  }
});

// Express route to insert a new review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  let data = JSON.parse(req.body);

  // Find the highest existing id
  const documents = await Reviews.find().sort({ id: -1 });
  let new_id = 1;
  if (documents.length > 0) {
    new_id = documents[0].id + 1;
  }

  const review = new Reviews({
    id: new_id,
    name: data.name,
    dealership: data.dealership,
    review: data.review,
    purchase: data.purchase,
    purchase_date: data.purchase_date,
    car_make: data.car_make,
    car_model: data.car_model,
    car_year: data.car_year
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
