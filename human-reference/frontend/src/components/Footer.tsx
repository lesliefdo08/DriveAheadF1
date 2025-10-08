import Link from "next/link";

export default function Footer() {
	return (
		<footer className="my-8 text-sm text-zinc-500">
			<div className="mb-4 flex flex-wrap gap-2">
				<p>
					Made with ♥ by <TextLink website="https://github.com/KennethJF23">Kenneth Fernandes</TextLink>,
					<TextLink website="https://github.com/glennfernando"> Verena Fernandes</TextLink>,
					<TextLink website="https://github.com/glennfernando"> Glenn Fernando </TextLink> and
					<TextLink website="https://github.com/lesliefdo08/"> Leslie Fernando</TextLink>.
				</p>

				<p>
					Contribute on <TextLink website="https://github.com/glennfernando/f1-dart">GitHub</TextLink>.
				</p>

				<p>
					Get{" "}
					<Link className="text-blue-500" href="/help">
						Help
					</Link>
					.
				</p>

				<p>Version: {process.env.version}</p>
			</div>

			<p>
				This project/website is unofficial and is not associated in any way with the Formula 1 companies. F1, FORMULA
				ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trademarks of Formula One
				Licensing B.V.
			</p>
		</footer>
	);
}

type TextLinkProps = {
	website: string;
	children: string;
};

const TextLink = ({ website, children }: TextLinkProps) => {
	return (
		<a className="text-blue-500" target="_blank" href={website}>
			{children}
		</a>
	);
};
