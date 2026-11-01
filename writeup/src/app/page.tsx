import Article from "@/components/article";

export default function Page() {
  return (
    <>
      <a className="skip-link" href="#writeup-start">
        Skip to write-up
      </a>
      <main>
        <Article />
      </main>
    </>
  );
}
