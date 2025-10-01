Build the minimal Flutter web app (quick demo)

1. Ensure Flutter is installed and on PATH.

2. From the project root run:

   cd frontend
   flutter pub get

3. Build the minimal entrypoint:

   flutter build web --release -t lib/main_minimal.dart

4. Serve the output from `frontend/build/web` (any static server). Example:

   cd frontend/build/web
   python3 -m http.server 3000

The minimal app hits the local Node mock backend at http://localhost:8080/ai-input by default.
