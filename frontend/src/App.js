// src/App.js
import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import MainPage from "./pages/MainPage";
// ... Import other pages

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/login" component={LoginPage} />
        <Route path="/signup" component={SignupPage} />
        <Route path="/main" component={MainPage} />
        <PrivateRoute path="/main" component={MainPage} />
        {/* ... Other routes */}
        <Route path="/" exact component={WelcomePage} />
      </Switch>
    </Router>
  );
}

export default App;
