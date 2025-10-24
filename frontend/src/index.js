import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from 'react-redux';
import 'react-quill/dist/quill.snow.css';
import "jsvectormap/dist/css/jsvectormap.css";
import 'react-toastify/dist/ReactToastify.css';
import 'react-modal-video/css/modal-video.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import { ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

import App from "./App";
import reportWebVitals from "./reportWebVitals";
import store from './store'; // Import your Redux store

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
       <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} newestOnTop={false} closeOnClick pauseOnFocusLoss draggable pauseOnHover />
    </Provider>
  </React.StrictMode>
);

reportWebVitals();