import {
  BookText,
  Boxes,
  Database,
  ExternalLink,
  Github,
  Newspaper,
  Quote,
  Star,
  type LucideIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { ResearchResult } from "@/lib/types";
import { formatCompact, formatDate, truncate } from "@/lib/utils";

function ExternalCard({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="group block h-full rounded-2xl border-2 border-pink-200 bg-white/80 p-4 shadow-candy transition-all duration-300 hover:-translate-y-0.5 hover:border-pink-400 hover:shadow-candy-lg"
    >
      {children}
    </a>
  );
}

function SectionHeading({
  icon: Icon,
  title,
  count,
}: {
  icon: LucideIcon;
  title: string;
  count: number;
}) {
  return (
    <div className="mb-3 flex items-center gap-2">
      <Icon className="h-4 w-4 text-pink-400" aria-hidden="true" />
      <h3 className="text-sm font-bold uppercase tracking-wider text-pink-500">{title}</h3>
      <Badge variant="secondary">{count}</Badge>
    </div>
  );
}

function CardTitleRow({ title }: { title: string }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <p className="text-sm font-semibold leading-snug text-pink-800 group-hover:text-pink-600">
        {title}
      </p>
      <ExternalLink
        className="mt-0.5 h-3.5 w-3.5 shrink-0 text-pink-300 group-hover:text-pink-500"
        aria-hidden="true"
      />
    </div>
  );
}

export interface SourcesPanelProps {
  result: ResearchResult;
}

export function SourcesPanel({ result }: SourcesPanelProps) {
  const { papers, news, github_repos, huggingface_models, datasets, citations } = result;
  const total =
    papers.length + news.length + github_repos.length + huggingface_models.length + datasets.length;

  if (total === 0 && citations.length === 0) {
    return (
      <Card>
        <CardContent className="p-10 text-center text-sm text-pink-400">
          No sources were collected for this topic.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-10">
      {papers.length > 0 && (
        <section>
          <SectionHeading icon={BookText} title="Research papers" count={papers.length} />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {papers.map((paper, i) => (
              <ExternalCard key={`${paper.url}-${i}`} href={paper.url}>
                <CardTitleRow title={paper.title} />
                <p className="mt-1 text-xs text-pink-400">
                  {paper.authors.slice(0, 4).join(", ")}
                  {paper.authors.length > 4 && " et al."}
                  {paper.year !== null && ` · ${paper.year}`}
                </p>
                {paper.abstract && (
                  <p className="mt-2 text-xs leading-5 text-pink-500/90">
                    {truncate(paper.abstract, 220)}
                  </p>
                )}
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="outline">{paper.source}</Badge>
                  {paper.citations !== null && (
                    <Badge variant="info">
                      <Quote className="h-3 w-3" aria-hidden="true" />
                      {formatCompact(paper.citations)} citations
                    </Badge>
                  )}
                </div>
              </ExternalCard>
            ))}
          </div>
        </section>
      )}

      {news.length > 0 && (
        <section>
          <SectionHeading icon={Newspaper} title="News coverage" count={news.length} />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {news.map((item, i) => (
              <ExternalCard key={`${item.url}-${i}`} href={item.url}>
                <CardTitleRow title={item.title} />
                <p className="mt-1 text-xs text-pink-400">
                  {item.source} · {formatDate(item.published_at)}
                </p>
                {item.summary && (
                  <p className="mt-2 text-xs leading-5 text-pink-500/90">
                    {truncate(item.summary, 200)}
                  </p>
                )}
              </ExternalCard>
            ))}
          </div>
        </section>
      )}

      {github_repos.length > 0 && (
        <section>
          <SectionHeading icon={Github} title="GitHub repositories" count={github_repos.length} />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {github_repos.map((repo, i) => (
              <ExternalCard key={`${repo.url}-${i}`} href={repo.url}>
                <CardTitleRow title={repo.name} />
                {repo.description && (
                  <p className="mt-2 text-xs leading-5 text-pink-500/90">
                    {truncate(repo.description, 140)}
                  </p>
                )}
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="warning">
                    <Star className="h-3 w-3" aria-hidden="true" />
                    {formatCompact(repo.stars)}
                  </Badge>
                  {repo.language && <Badge variant="outline">{repo.language}</Badge>}
                </div>
              </ExternalCard>
            ))}
          </div>
        </section>
      )}

      {huggingface_models.length > 0 && (
        <section>
          <SectionHeading icon={Boxes} title="Hugging Face models" count={huggingface_models.length} />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {huggingface_models.map((model, i) => (
              <ExternalCard key={`${model.url}-${i}`} href={model.url}>
                <CardTitleRow title={model.id} />
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="info">{formatCompact(model.downloads)} downloads</Badge>
                  <Badge variant="secondary">{formatCompact(model.likes)} likes</Badge>
                  {model.task && <Badge variant="outline">{model.task}</Badge>}
                </div>
              </ExternalCard>
            ))}
          </div>
        </section>
      )}

      {datasets.length > 0 && (
        <section>
          <SectionHeading icon={Database} title="Datasets" count={datasets.length} />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {datasets.map((dataset, i) => (
              <ExternalCard key={`${dataset.url}-${i}`} href={dataset.url}>
                <CardTitleRow title={dataset.name} />
                {dataset.description && (
                  <p className="mt-2 text-xs leading-5 text-pink-500/90">
                    {truncate(dataset.description, 140)}
                  </p>
                )}
                <div className="mt-3">
                  <Badge variant="outline">{dataset.source}</Badge>
                </div>
              </ExternalCard>
            ))}
          </div>
        </section>
      )}

      {citations.length > 0 && (
        <section>
          <SectionHeading icon={Quote} title="Citations" count={citations.length} />
          <ol className="space-y-2">
            {citations.map((citation) => (
              <li
                key={citation.id}
                className="flex items-start gap-3 rounded-2xl border-2 border-pink-200 bg-white/80 px-3 py-2.5"
              >
                <Badge className="mt-0.5 shrink-0 tabular-nums">[{citation.id}]</Badge>
                <div className="min-w-0">
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-pink-800 underline-offset-2 hover:text-fuchsia-600 hover:underline"
                  >
                    {citation.title}
                  </a>
                  <p className="text-xs text-pink-400">{citation.source}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
