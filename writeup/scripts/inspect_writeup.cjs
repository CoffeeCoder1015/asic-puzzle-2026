const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");

async function inspect(source) {
  const remote = /^https?:\/\//.test(source);
  const html = remote
    ? await (await fetch(source)).text()
    : await fs.readFile(source, "utf8");
  const images = [];

  for (const match of html.matchAll(/<img[^>]+src="([^"]+)"[^>]*>/g)) {
    const src = match[1];
    let bytes;
    if (src.startsWith("data:")) {
      bytes = Buffer.from(src.slice(src.indexOf(",") + 1), "base64");
    } else if (remote) {
      bytes = Buffer.from(
        await (await fetch(new URL(src, source))).arrayBuffer(),
      );
    } else {
      bytes = await fs.readFile(path.resolve(path.dirname(source), src));
    }
    images.push(crypto.createHash("sha256").update(bytes).digest("hex"));
  }

  const streams = [
    ...new Set([...html.matchAll(/[01]{121}/g)].map((match) => match[0])),
  ];
  const headings = [...html.matchAll(/<h[12][^>]*>([\s\S]*?)<\/h[12]>/g)].map(
    (match) => match[1].replace(/<[^>]+>/g, "").trim(),
  );
  return { source, images, streams, headings };
}

async function main() {
  const current = await inspect(process.argv[2] || "http://127.0.0.1:3001");
  if (process.argv[3]) {
    const reference = await inspect(process.argv[3]);
    current.comparison = {
      scientificImagesUnchanged:
        JSON.stringify(current.images) === JSON.stringify(reference.images),
      exactInputStreamsUnchanged:
        JSON.stringify([...current.streams].sort()) ===
        JSON.stringify([...reference.streams].sort()),
    };
  }
  console.log(JSON.stringify(current, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
