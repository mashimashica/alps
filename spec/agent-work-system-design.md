# Design Principles for Agent Work Systems

[Japanese translation](locales/ja/agent-work-system-design.md)

## 1. Scope and terms

These principles concern the design of systems that use agents to perform work. An **Agent Work System** is defined here as a combination of agents, the tools, information resources, and execution environment needed for their work, and the interactions among them. The design objective is a configuration that can achieve the intended results under the applicable conditions.

An **agent** interprets the situation and selects or constructs a way to proceed toward the intended results. A **tool** exposes a processing capability through an interface with a defined role and conditions of use. **Information resources** provide information needed to interpret, perform, or assess work. The **execution environment** provides the facilities and conditions under which the components operate. These roles can coexist within a component; the relevant responsibilities and interactions must remain clear.

**Must** expresses a requirement, **must not** a prohibition, **should** a recommendation, and **may** permission. Requirements apply within their stated scope. The required extent of design and evaluation depends on the work, its consequences, and the requested scope.

## 2. Responsibilities and allocation

The design must identify the intended results, applicable conditions, and capabilities needed to perform the work. It must allocate responsibilities across agents, tools, information resources, and the execution environment, making dependencies and interactions clear enough to realize and assess the configuration.

Context-dependent interpretation, selection, and composition should remain with an agent where judgment is needed. Established calculations, transformations, checks, selection rules, and sequences should be implemented when a suitable implementation can perform them reliably. An agent can bridge the intended results and available means by selecting and combining capabilities, adapting a method, or devising and implementing a new method or tool within the authorized scope.

Existing capabilities should be assessed for fitness before new ones are built. Allocation decisions must consider the actual capabilities and limitations of the components, the information available to them, and the consequences of error. Responsibility for interpreting results and responding to failure must be assigned as well as responsibility for producing results.

## 3. Boundaries and composition

Component boundaries should group responsibilities that belong together and hide internal decisions that other components do not need to know. Interfaces should expose the information and operations needed for use, verification, and composition while limiting the effects of internal changes on their users. Cohesion, coupling, and the effects of change should guide decomposition.

Internal module boundaries and operations exposed to an agent serve different purposes. A stable combination of internal operations should be offered as one tool operation when that reduces unnecessary selection and coordination without removing a meaningful choice. Combinations that depend on the situation should remain selectable at the point where the necessary information and judgment are available.

The size of a component or public operation should be judged by the clarity of its responsibility and its ease of use, verification, change, and composition. The design may use one agent and existing tools when that is sufficient.

## 4. Information and interfaces

Agents and tools must be able to obtain the information required for their responsibilities. The design must make the sources, meaning, applicability, and relevant freshness of that information clear. Selecting or summarizing information must preserve what is needed for the dependent decision, including material uncertainty and provenance.

For each required tool operation, the design must make the following clear to its users, to the extent needed for correct use:

- Its responsibility, applicable conditions, and limits.
- How to invoke it, including the meaning of arguments and returned information.
- Required resources and dependencies, including environment assumptions.
- How successful processing, failed processing, and incomplete results are distinguished, and how they inform the next action.
- For changes to external state, the affected state, possible effects, and conditions for retrying or continuing after partial completion.

Descriptions and responses should enable users to distinguish operations with different purposes or conditions. Responses should supply sufficient, relevant evidence for subsequent decisions. Missing information, truncation, or an uncertain effect must be visible where it affects interpretation.

When interaction fails, the design should consider improvements to the tools, information supply, and environment as well as the instructions given to the agent.

## 5. Execution conditions and effects

The design must identify the execution conditions on which its claims depend, including access, dependencies, available capabilities, and any required authority or approval. Required conditions must be confirmed before the actions or claims that depend on them. A missing or unconfirmed condition must limit dependent actions and judgments; independent work may proceed under its own applicable conditions.

A tool may use external services, changing state, or probabilistic processing. Its interface must communicate the guarantees and limits relevant to its use. Where determinism or reproducibility is needed, the design must identify what must be repeatable and the inputs, versions, state, and environment conditions needed to support that claim.

Error handling must account for possible effects already produced. Before retrying a state-changing operation whose result is uncertain, the system must ascertain the resulting state or use a recovery mechanism that supports the intended retry. Evidence of successful tool processing must be interpreted against the intended result and applicable conditions.

## 6. Evaluation

Evaluation must identify its subject, criteria, evidence, and scope. It must distinguish:

1. Whether the design's responsibilities, relationships, and applicable conditions are coherent and sufficient.
2. Whether the components and their connections meet their specified behavior under the relevant conditions.
3. Whether the system performs representative work effectively, using the intended agent, information, tools, and environment.

Checks must cover relevant successful, failed, and incomplete interactions and the connections on which the work depends. End-to-end evaluation must assess the intended results and applicable conditions using evidence from the work. An artifact's existence or a tool's successful completion alone does not establish effectiveness.

The evaluation must identify assumptions, unresolved findings, unperformed checks, and limits of the tested cases. Evidence from a component test or a representative application supports a judgment within its examined scope. Findings should inform changes to the allocation of responsibilities, interfaces, information, or environment where those changes address the cause.

## 7. Adaptation

Changes in model, tool, or environment capabilities should trigger review of the affected allocation, instructions, information supply, and exposed operations. The review must distinguish guidance compensating for a capability limitation from knowledge, criteria, and constraints required by the work itself.

Proposed changes must preserve the intended results and applicable conditions or explicitly establish and justify changes to them. Affected behavior must be re-evaluated through the relevant component checks and representative work before relying on the changed configuration. The scope and limits of the resulting evidence must remain explicit.

## Informative sources

The principles above are an independent design formulation. The definition of Agent Work System is specific to this document. ISO 6385 informs the attention to the whole work system and function allocation; its human ergonomics requirements are not transferred to agents, and this document makes no claim of applying or conforming to that standard as a whole.

| Source and kind | Edition and passages used |
| --- | --- |
| [ISO 6385:2016](https://www.iso.org/standard/63785.html), ergonomics standard | Third edition, 2016-09-15; scope, definitions of work system, work equipment, and allocation of functions (§§1, 2.2, 2.6, 2.15), and general design principles (§3.1), checked in the [public preview](https://cdn.standards.iteh.ai/samples/63785/29a50db0a6d048208c063c308b21f500/ISO-6385-2016.pdf). |
| Eric S. Raymond, [The Art of Unix Programming](https://www.catb.org/esr/writings/taoup/html/), book | Published 2003; [publisher sample](https://ptgmedia.pearsoncmg.com/images/9780131429017/samplepages/0131429019.pdf), sixth printing September 2008, Chapter 1 §§1.6.1, 1.6.3, 1.6.4 (pp. 14–17): modularity, composition, and separation. |
| IEEE Computer Society, [SWEBOK Guide](https://www.computer.org/education/bodies-of-knowledge/software-engineering), body of knowledge guide | [Version 4.0a, released August 2026](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf); Chapter 3, §1.4 design principles, §2.1 interactions, and §§6.1–6.3 design quality and evaluation. |
| Karun Japhet, Sahaj, [The Unix Philosophy for Agentic Coding](https://www.sahaj.ai/the-unix-philosophy-for-agentic-coding/), practice article | Undated online text; “The Pattern,” examples, and “Skills, Hooks, and Tools”: existing capabilities, small purpose-built tools, and agent composition. |
| Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), practice article | Dated 2024-12-19, current online text; “What are agents?”, “When (and when not) to use agents,” and tool engineering in Appendix 2. |
| Anthropic, [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents), practice article | Dated 2025-09-11; evaluation, choosing tools, meaningful context, and tool descriptions. |

Online sources were consulted on 2026-09-06. The book, guide, and practice articles inform responsibility boundaries, interfaces, composition, and evaluation; they do not define the requirements of this document.
