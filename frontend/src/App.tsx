/**
 * Root router: Landing at /, Console (and flow view) at /console and /console/flow/:id.
 * Function-first: primary experience is the console after landing.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { Console } from './pages/Console';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/console" element={<Console />} />
      <Route path="/console/flow/:id" element={<Console />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
