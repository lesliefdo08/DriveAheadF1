export default function Footer() {
  return (
    <footer className="bg-black border-t border-white/10 py-12 mt-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-f1 text-lg font-bold mb-4">DriveAhead F1</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Advanced Formula 1 analytics platform powered by machine learning and real-time data.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-f1 text-lg font-bold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <a href="/predictions" className="text-gray-400 hover:text-white transition-colors text-sm">
                  <i className="fas fa-chart-line mr-2"></i>
                  Race Predictions
                </a>
              </li>
              <li>
                <a href="/standings" className="text-gray-400 hover:text-white transition-colors text-sm">
                  <i className="fas fa-trophy mr-2"></i>
                  Standings
                </a>
              </li>
              <li>
                <a href="/telemetry" className="text-gray-400 hover:text-white transition-colors text-sm">
                  <i className="fas fa-broadcast-tower mr-2"></i>
                  Live Telemetry
                </a>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h3 className="text-white font-f1 text-lg font-bold mb-4">Technology</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Built with Next.js, React, Flask, and powered by advanced machine learning algorithms.
            </p>
            <div className="flex space-x-4 mt-4">
              <span className="text-f1-red text-xs font-semibold bg-f1-red/10 px-3 py-1 rounded-full">ML Powered</span>
              <span className="text-f1-blue text-xs font-semibold bg-f1-blue/10 px-3 py-1 rounded-full">Real-time</span>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-white/10 mt-8 pt-8 text-center">
          <p className="text-gray-500 text-sm">
            © {new Date().getFullYear()} DriveAhead F1 Analytics. All rights reserved.
          </p>
          <p className="text-gray-600 text-xs mt-2">
            Data provided by Jolpica F1 API. Not affiliated with Formula 1.
          </p>
        </div>
      </div>
    </footer>
  );
}
