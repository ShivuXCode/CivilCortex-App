# Phase 12: Frontend Foundation and Core UI Shell

This phase established the actual React frontend for CivilCortex, converting the previous skeleton to a strict TypeScript codebase powered by Tailwind CSS.

## Architecture

- **Framework**: Vite + React 19 + TypeScript
- **Routing**: `react-router-dom` with authenticated boundary protecting internal routes.
- **Styling**: Tailwind CSS v4 via `@tailwindcss/vite` plugin, utilizing a custom civil engineering design system.
- **API Client**: Axios instance configured with a JWT request interceptor (`Bearer`) and a 401 unauthorized response interceptor that automatically redirects to login.

## Implemented Pages

1. **Login** (`/login`): Clean authentication form capturing the username (email) and password, exchanging it against `POST /auth/login` for the JWT token.
2. **Dashboard** (`/dashboard`): High-level view showing total buildings, active inspections, and open defects (currently placeholder text as requested to prevent fabricating data), with quick action buttons.
3. **Buildings** (`/buildings`, `/buildings/:id`): List of available structures and detail view displaying the complete `Floor > Area > Structural Element` hierarchy mapped from the backend.
4. **New Inspection** (`/inspections/new`): A multi-step wizard allowing users to:
   - Select the exact physical location (`Building -> Floor -> Area -> Element`).
   - Upload an image (`POST /inspections/{id}/images`).
   - Run the development ML model (`POST /inspections/{id}/images/{img_id}/analyze`).
   - Review the result clearly marked as `DEVELOPMENT` model requiring engineering review.
   - Save the final `Defect` and `CrackObservation` to the database.
5. **Defect Register** (`/defects`): A clean tabular view of all recorded defects and their statuses, filtered strictly to the user's ownership hierarchy.

## Backend Modifications

During implementation, two minor backend additions were made to support the UI:
1. `GET /api/v1/hierarchy/buildings/{id}`: Added a detail endpoint returning a building deeply nested with its floors, areas, and structural elements.
2. `GET /api/v1/defects/`: Added an endpoint to fetch defects owned by the current user across all buildings.
