import type { Metadata } from "next";

const title = "Drive Ahead Realtime Telemetry | Formula 1 live timing, prediction and analytics dashboard";
const description =
	"Experience live telemetry and timing data from Formula 1 races. Get insights into leaderboards, tire choices, gaps, lap times, sector times, team radios, and more.";

const url = "https://f1-dash.com";

export const metadata: Metadata = {
	generator: "Next.js",

	applicationName: title,

	title,
	description,

	openGraph: {
		title,
		description,
		url,
		type: "website",
		siteName: "Drive Ahead Realtime Telemetry",
		images: [
			{
				alt: "DART - Drive Ahead Realtime Telemetry",
				url: `${url}/og-image.png`,
				width: 1200,
				height: 630,
			},
		],
	},

	category: "Sports & Recreation",

	referrer: "strict-origin-when-cross-origin",

	keywords: ["Formula 1", "f1 dashboard", "realtime telemetry", "f1 timing", "live updates", "f1 analytics", "f1 prediction"],

	creator: "TEA16",
	publisher: "TEA16",
	authors: [{ name: "TEA16", url: "https://tea16.dev" }],

	appleWebApp: {
		capable: true,
		title: "Drive Ahead Realtime Telemetry",
		statusBarStyle: "black-translucent",
	},

	formatDetection: {
		email: false,
		address: false,
		telephone: false,
	},

	metadataBase: new URL(url),

	alternates: {
		canonical: url,
	},

	// verification: {
	// 	google: "hKv0h7XtWgQ-pVNVKpwwb2wcCC2f0tBQ1X1IcDX50hg",
	// },

	manifest: "/manifest.json",
};
