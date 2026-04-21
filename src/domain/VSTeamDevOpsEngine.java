// ===========================================================================
// OMNI DOMAIN LAYER — VSTEAM DEVOPS ENGINE
// ===========================================================================
// Source Repo   : github.com/MethodsAndPractices/vsteam
// Domain Layer  : Domain (CI/CD automation, project management)
// Language      : Java
// Function      : Azure DevOps REST API automation — project lifecycle CRUD,
//                 build/release pipeline management, work item tracking with
//                 Agile state machine, Git repository management, pull request
//                 workflow, team/member RBAC, file-system-like resource
//                 navigation (VSTeamDrive), service endpoint management,
//                 and cross-project analytics.
// ===========================================================================

package OmniDomain.VSTeam;

import java.time.Instant;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

// ---- Project Visibility ---------------------------------------------------

enum ProjectVisibility {
    PRIVATE, PUBLIC
}

// ---- Process Template -----------------------------------------------------

enum ProcessTemplate {
    AGILE("Agile", "adcc42ab-9882-485e-a3ed-7678f01f66bc"),
    SCRUM("Scrum", "6b724908-ef14-45cf-84f8-768b5384da45"),
    CMMI("CMMI", "27450541-8e31-4150-9947-dc59f998fc01"),
    BASIC("Basic", "b8a3a935-7e91-48b8-a94c-606d37c3e9f2");

    final String displayName;
    final String templateId;
    ProcessTemplate(String name, String id) {
        this.displayName = name;
        this.templateId = id;
    }
}

// ---- Work Item Type -------------------------------------------------------

enum WorkItemType {
    EPIC, FEATURE, USER_STORY, TASK, BUG, TEST_CASE, IMPEDIMENT
}

// ---- Work Item State Machine (Agile) --------------------------------------

enum WorkItemState {
    NEW, ACTIVE, RESOLVED, CLOSED, REMOVED;

    boolean canTransitionTo(WorkItemState target) {
        switch (this) {
            case NEW:      return target == ACTIVE || target == REMOVED;
            case ACTIVE:   return target == RESOLVED || target == CLOSED || target == REMOVED;
            case RESOLVED: return target == ACTIVE || target == CLOSED;
            case CLOSED:   return target == ACTIVE;
            case REMOVED:  return false;
            default:       return false;
        }
    }
}

// ---- Build Status ---------------------------------------------------------

enum BuildStatus {
    NONE, IN_PROGRESS, COMPLETED, CANCELLING, POSTPONED, NOT_STARTED
}

enum BuildResult {
    NONE, SUCCEEDED, PARTIAL_SUCCESS, FAILED, CANCELED
}

// ---- Release Status -------------------------------------------------------

enum ReleaseStatus {
    ACTIVE, DRAFT, ABANDONED, UNDEFINED
}

enum DeploymentStatus {
    UNDEFINED, NOT_DEPLOYED, IN_PROGRESS, SUCCEEDED, PARTIAL_SUCCESS, FAILED
}

// ---- PR Status ------------------------------------------------------------

enum PRStatus {
    ACTIVE, ABANDONED, COMPLETED;
}

enum PRVote {
    APPROVE(10), APPROVE_WITH_SUGGESTIONS(5), NO_VOTE(0),
    WAIT_FOR_AUTHOR(-5), REJECT(-10);

    final int value;
    PRVote(int v) { this.value = v; }
}

// ---- Data Objects ---------------------------------------------------------

class DevOpsProject {
    final String id;
    final String name;
    String description;
    ProjectVisibility visibility;
    ProcessTemplate process;
    Instant createdDate;
    String state; // "wellFormed", "createPending", "deleting"
    Map<String, String> properties;

    DevOpsProject(String id, String name, ProcessTemplate process) {
        this.id = id;
        this.name = name;
        this.process = process;
        this.visibility = ProjectVisibility.PRIVATE;
        this.state = "wellFormed";
        this.createdDate = Instant.now();
        this.properties = new HashMap<>();
    }
}

class BuildDefinition {
    final String id;
    String name;
    String projectId;
    String repository;
    String defaultBranch;
    String yamlPath;
    boolean enabled;
    Map<String, String> variables;
    List<String> triggers; // "ci", "schedule", "pullRequest"
    int retentionDays;
    Instant createdDate;

    BuildDefinition(String id, String name, String projectId) {
        this.id = id;
        this.name = name;
        this.projectId = projectId;
        this.defaultBranch = "refs/heads/main";
        this.yamlPath = "/azure-pipelines.yml";
        this.enabled = true;
        this.variables = new HashMap<>();
        this.triggers = new ArrayList<>(List.of("ci"));
        this.retentionDays = 30;
        this.createdDate = Instant.now();
    }
}

class BuildRun {
    final String id;
    String definitionId;
    String projectId;
    BuildStatus status;
    BuildResult result;
    String sourceBranch;
    String sourceVersion;
    Instant startTime;
    Instant finishTime;
    String requestedBy;
    int buildNumber;
    List<String> logs;

    BuildRun(String id, String definitionId, String projectId) {
        this.id = id;
        this.definitionId = definitionId;
        this.projectId = projectId;
        this.status = BuildStatus.NOT_STARTED;
        this.result = BuildResult.NONE;
        this.sourceBranch = "refs/heads/main";
        this.startTime = Instant.now();
        this.buildNumber = 0;
        this.logs = new ArrayList<>();
    }
}

class ReleaseDefinition {
    final String id;
    String name;
    String projectId;
    List<ReleaseEnvironment> environments;
    Map<String, String> variables;
    String artifactSource; // build definition id
    ReleaseStatus status;
    Instant createdDate;

    ReleaseDefinition(String id, String name, String projectId) {
        this.id = id;
        this.name = name;
        this.projectId = projectId;
        this.environments = new ArrayList<>();
        this.variables = new HashMap<>();
        this.status = ReleaseStatus.DRAFT;
        this.createdDate = Instant.now();
    }
}

class ReleaseEnvironment {
    String name;          // "Dev", "Staging", "Production"
    DeploymentStatus deploymentStatus;
    int rank;             // execution order
    String preApprover;   // required approver before deployment
    String postApprover;
    Map<String, String> variables;

    ReleaseEnvironment(String name, int rank) {
        this.name = name;
        this.rank = rank;
        this.deploymentStatus = DeploymentStatus.UNDEFINED;
        this.variables = new HashMap<>();
    }
}

class WorkItem {
    final String id;
    WorkItemType type;
    String title;
    String description;
    WorkItemState state;
    String assignedTo;
    String projectId;
    int priority;       // 1-4 (1 = highest)
    double effort;      // story points or hours
    String areaPath;
    String iterationPath;
    String parentId;
    List<String> tags;
    List<WorkItemComment> comments;
    Instant createdDate;
    Instant changedDate;

    WorkItem(String id, WorkItemType type, String title, String projectId) {
        this.id = id;
        this.type = type;
        this.title = title;
        this.projectId = projectId;
        this.state = WorkItemState.NEW;
        this.priority = 2;
        this.tags = new ArrayList<>();
        this.comments = new ArrayList<>();
        this.createdDate = Instant.now();
        this.changedDate = Instant.now();
    }

    boolean transitionTo(WorkItemState newState) {
        if (state.canTransitionTo(newState)) {
            state = newState;
            changedDate = Instant.now();
            return true;
        }
        return false;
    }
}

class WorkItemComment {
    String author;
    String text;
    Instant timestamp;

    WorkItemComment(String author, String text) {
        this.author = author;
        this.text = text;
        this.timestamp = Instant.now();
    }
}

class GitRepository {
    final String id;
    String name;
    String projectId;
    String defaultBranch;
    long sizeBytes;
    String remoteUrl;
    List<String> branches;
    Instant createdDate;

    GitRepository(String id, String name, String projectId) {
        this.id = id;
        this.name = name;
        this.projectId = projectId;
        this.defaultBranch = "refs/heads/main";
        this.branches = new ArrayList<>(List.of("main", "develop"));
        this.createdDate = Instant.now();
    }
}

class PullRequest {
    final String id;
    String repositoryId;
    String projectId;
    String title;
    String description;
    String sourceBranch;
    String targetBranch;
    PRStatus status;
    String createdBy;
    List<PRReviewer> reviewers;
    List<String> labels;
    boolean isDraft;
    boolean autoComplete;
    Instant createdDate;
    Instant closedDate;

    PullRequest(String id, String repoId, String projectId, String title) {
        this.id = id;
        this.repositoryId = repoId;
        this.projectId = projectId;
        this.title = title;
        this.status = PRStatus.ACTIVE;
        this.sourceBranch = "refs/heads/feature";
        this.targetBranch = "refs/heads/main";
        this.reviewers = new ArrayList<>();
        this.labels = new ArrayList<>();
        this.createdDate = Instant.now();
    }
}

class PRReviewer {
    String displayName;
    String email;
    PRVote vote;

    PRReviewer(String name, String email) {
        this.displayName = name;
        this.email = email;
        this.vote = PRVote.NO_VOTE;
    }
}

class TeamMember {
    final String id;
    String displayName;
    String email;
    String role;           // "projectAdmin", "contributor", "reader"
    boolean isTeamAdmin;
    List<String> teamIds;

    TeamMember(String id, String name, String email, String role) {
        this.id = id;
        this.displayName = name;
        this.email = email;
        this.role = role;
        this.isTeamAdmin = false;
        this.teamIds = new ArrayList<>();
    }
}

class ServiceEndpoint {
    final String id;
    String name;
    String type;    // "github", "azurerm", "docker", "kubernetes", "generic"
    String url;
    boolean isReady;
    String owner;
    Map<String, String> authorization;
    Instant createdDate;

    ServiceEndpoint(String id, String name, String type, String url) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.url = url;
        this.isReady = true;
        this.authorization = new HashMap<>();
        this.createdDate = Instant.now();
    }
}

// ---- VSTeam Drive Node (File-system-like nav) -----------------------------

class DriveNode {
    String name;
    String path;
    String type;  // "organization", "project", "area", "item"
    List<DriveNode> children;

    DriveNode(String name, String path, String type) {
        this.name = name;
        this.path = path;
        this.type = type;
        this.children = new ArrayList<>();
    }

    DriveNode addChild(String childName, String childType) {
        DriveNode child = new DriveNode(childName, path + "/" + childName, childType);
        children.add(child);
        return child;
    }

    List<String> listChildren() {
        return children.stream().map(c -> c.name + " (" + c.type + ")").collect(Collectors.toList());
    }
}

// ---- VSTeam DevOps Engine (Main Orchestrator) -----------------------------

public class VSTeamDevOpsEngine {
    private final String organizationUrl;
    private String personalAccessToken;

    private final Map<String, DevOpsProject> projects = new ConcurrentHashMap<>();
    private final Map<String, BuildDefinition> buildDefs = new ConcurrentHashMap<>();
    private final Map<String, BuildRun> buildRuns = new ConcurrentHashMap<>();
    private final Map<String, ReleaseDefinition> releaseDefs = new ConcurrentHashMap<>();
    private final Map<String, WorkItem> workItems = new ConcurrentHashMap<>();
    private final Map<String, GitRepository> gitRepos = new ConcurrentHashMap<>();
    private final Map<String, PullRequest> pullRequests = new ConcurrentHashMap<>();
    private final Map<String, TeamMember> members = new ConcurrentHashMap<>();
    private final Map<String, ServiceEndpoint> endpoints = new ConcurrentHashMap<>();

    private int idCounter = 1000;

    public VSTeamDevOpsEngine(String organizationUrl, String pat) {
        this.organizationUrl = organizationUrl;
        this.personalAccessToken = pat;
        System.out.printf("[VSTEAM-OMNI-JAVA] DevOps engine initialized: %s%n", organizationUrl);
    }

    private String nextId(String prefix) {
        return prefix + "-" + (++idCounter);
    }

    // ---- Project Management -----------------------------------------------

    public DevOpsProject createProject(String name, String description, ProcessTemplate process) {
        String id = nextId("proj");
        DevOpsProject p = new DevOpsProject(id, name, process);
        p.description = description;
        projects.put(id, p);

        // Auto-create default repository
        createRepository(id, name);

        System.out.printf("[VSTEAM-OMNI-JAVA] Project created: %s (%s, %s)%n",
                name, process.displayName, id);
        return p;
    }

    public DevOpsProject getProject(String projectId) {
        return projects.get(projectId);
    }

    public void deleteProject(String projectId) {
        DevOpsProject p = projects.remove(projectId);
        if (p != null) {
            System.out.printf("[VSTEAM-OMNI-JAVA] Project deleted: %s%n", p.name);
        }
    }

    public List<DevOpsProject> listProjects() {
        return new ArrayList<>(projects.values());
    }

    // ---- Build Pipeline Management ----------------------------------------

    public BuildDefinition createBuildDefinition(
            String projectId, String name, String yamlPath, String branch) {
        String id = nextId("bdef");
        BuildDefinition bd = new BuildDefinition(id, name, projectId);
        bd.yamlPath = yamlPath;
        bd.defaultBranch = "refs/heads/" + branch;
        buildDefs.put(id, bd);

        System.out.printf("[VSTEAM-OMNI-JAVA] Build def created: %s (%s)%n", name, id);
        return bd;
    }

    public BuildRun queueBuild(String definitionId, String branch, String requestedBy) {
        BuildDefinition def = buildDefs.get(definitionId);
        if (def == null) throw new IllegalArgumentException("Build definition not found: " + definitionId);

        String id = nextId("build");
        BuildRun run = new BuildRun(id, definitionId, def.projectId);
        run.sourceBranch = "refs/heads/" + branch;
        run.requestedBy = requestedBy;
        run.status = BuildStatus.IN_PROGRESS;
        run.buildNumber = (int) (System.currentTimeMillis() % 100000);
        buildRuns.put(id, run);

        System.out.printf("[VSTEAM-OMNI-JAVA] Build queued: %s (#%d) on %s%n",
                def.name, run.buildNumber, branch);

        // Simulate build completion
        CompletableFuture.runAsync(() -> {
            try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
            run.status = BuildStatus.COMPLETED;
            run.result = BuildResult.SUCCEEDED;
            run.finishTime = Instant.now();
            run.logs.add("[1/5] Restoring packages...");
            run.logs.add("[2/5] Building solution...");
            run.logs.add("[3/5] Running tests...");
            run.logs.add("[4/5] Publishing artifacts...");
            run.logs.add("[5/5] Build succeeded.");
            System.out.printf("[VSTEAM-OMNI-JAVA] Build completed: #%d -> %s%n",
                    run.buildNumber, run.result);
        });

        return run;
    }

    public List<BuildRun> getBuildHistory(String definitionId, int top) {
        return buildRuns.values().stream()
                .filter(b -> b.definitionId.equals(definitionId))
                .sorted(Comparator.comparing((BuildRun b) -> b.startTime).reversed())
                .limit(top)
                .collect(Collectors.toList());
    }

    // ---- Release Pipeline Management --------------------------------------

    public ReleaseDefinition createReleaseDefinition(
            String projectId, String name, List<String> environmentNames) {
        String id = nextId("rdef");
        ReleaseDefinition rd = new ReleaseDefinition(id, name, projectId);
        for (int i = 0; i < environmentNames.size(); i++) {
            rd.environments.add(new ReleaseEnvironment(environmentNames.get(i), i + 1));
        }
        rd.status = ReleaseStatus.ACTIVE;
        releaseDefs.put(id, rd);

        System.out.printf("[VSTEAM-OMNI-JAVA] Release def created: %s (%d environments)%n",
                name, environmentNames.size());
        return rd;
    }

    public ReleaseEnvironment deployToEnvironment(String releaseDefId, String envName) {
        ReleaseDefinition rd = releaseDefs.get(releaseDefId);
        if (rd == null) throw new IllegalArgumentException("Release def not found");

        for (ReleaseEnvironment env : rd.environments) {
            if (env.name.equalsIgnoreCase(envName)) {
                env.deploymentStatus = DeploymentStatus.IN_PROGRESS;
                System.out.printf("[VSTEAM-OMNI-JAVA] Deploying to %s...%n", envName);

                // Simulate deployment
                CompletableFuture.runAsync(() -> {
                    try { Thread.sleep(3000); } catch (InterruptedException ignored) {}
                    env.deploymentStatus = DeploymentStatus.SUCCEEDED;
                    System.out.printf("[VSTEAM-OMNI-JAVA] Deployment to %s: SUCCEEDED%n", envName);
                });
                return env;
            }
        }
        throw new IllegalArgumentException("Environment not found: " + envName);
    }

    // ---- Work Item Management ---------------------------------------------

    public WorkItem createWorkItem(String projectId, WorkItemType type, String title) {
        String id = nextId("wi");
        WorkItem wi = new WorkItem(id, type, title, projectId);
        workItems.put(id, wi);
        System.out.printf("[VSTEAM-OMNI-JAVA] Work item created: %s [%s] '%s'%n",
                id, type, title);
        return wi;
    }

    public boolean updateWorkItemState(String workItemId, WorkItemState newState) {
        WorkItem wi = workItems.get(workItemId);
        if (wi == null) return false;

        boolean transitioned = wi.transitionTo(newState);
        if (transitioned) {
            System.out.printf("[VSTEAM-OMNI-JAVA] Work item %s: %s -> %s%n",
                    workItemId, wi.state, newState);
        } else {
            System.out.printf("[VSTEAM-OMNI-JAVA] Invalid transition: %s -> %s%n",
                    wi.state, newState);
        }
        return transitioned;
    }

    public WorkItem assignWorkItem(String workItemId, String assignee) {
        WorkItem wi = workItems.get(workItemId);
        if (wi != null) {
            wi.assignedTo = assignee;
            wi.changedDate = Instant.now();
        }
        return wi;
    }

    public void addWorkItemComment(String workItemId, String author, String text) {
        WorkItem wi = workItems.get(workItemId);
        if (wi != null) {
            wi.comments.add(new WorkItemComment(author, text));
            wi.changedDate = Instant.now();
        }
    }

    public List<WorkItem> queryWorkItems(String projectId, WorkItemState state, WorkItemType type) {
        return workItems.values().stream()
                .filter(wi -> (projectId == null || wi.projectId.equals(projectId)))
                .filter(wi -> (state == null || wi.state == state))
                .filter(wi -> (type == null || wi.type == type))
                .sorted(Comparator.comparingInt(wi -> wi.priority))
                .collect(Collectors.toList());
    }

    // ---- Git Repository Management ----------------------------------------

    public GitRepository createRepository(String projectId, String name) {
        String id = nextId("repo");
        GitRepository repo = new GitRepository(id, name, projectId);
        repo.remoteUrl = organizationUrl + "/" + name + "/_git/" + name;
        gitRepos.put(id, repo);
        System.out.printf("[VSTEAM-OMNI-JAVA] Repository created: %s%n", name);
        return repo;
    }

    public void addBranch(String repoId, String branchName) {
        GitRepository repo = gitRepos.get(repoId);
        if (repo != null && !repo.branches.contains(branchName)) {
            repo.branches.add(branchName);
        }
    }

    // ---- Pull Request Management ------------------------------------------

    public PullRequest createPullRequest(
            String repoId, String title, String sourceBranch, String targetBranch) {
        GitRepository repo = gitRepos.get(repoId);
        if (repo == null) throw new IllegalArgumentException("Repository not found: " + repoId);

        String id = nextId("pr");
        PullRequest pr = new PullRequest(id, repoId, repo.projectId, title);
        pr.sourceBranch = "refs/heads/" + sourceBranch;
        pr.targetBranch = "refs/heads/" + targetBranch;
        pullRequests.put(id, pr);

        System.out.printf("[VSTEAM-OMNI-JAVA] PR created: #%s '%s' (%s -> %s)%n",
                id, title, sourceBranch, targetBranch);
        return pr;
    }

    public void addPRReviewer(String prId, String name, String email) {
        PullRequest pr = pullRequests.get(prId);
        if (pr != null) {
            pr.reviewers.add(new PRReviewer(name, email));
        }
    }

    public void votePR(String prId, String reviewerEmail, PRVote vote) {
        PullRequest pr = pullRequests.get(prId);
        if (pr == null) return;
        for (PRReviewer r : pr.reviewers) {
            if (r.email.equals(reviewerEmail)) {
                r.vote = vote;
                System.out.printf("[VSTEAM-OMNI-JAVA] PR %s: %s voted %s%n",
                        prId, r.displayName, vote);
                break;
            }
        }
    }

    public void completePR(String prId) {
        PullRequest pr = pullRequests.get(prId);
        if (pr != null) {
            pr.status = PRStatus.COMPLETED;
            pr.closedDate = Instant.now();
            System.out.printf("[VSTEAM-OMNI-JAVA] PR %s completed%n", prId);
        }
    }

    // ---- Team & Member Management -----------------------------------------

    public TeamMember addMember(String name, String email, String role) {
        String id = nextId("mem");
        TeamMember member = new TeamMember(id, name, email, role);
        members.put(id, member);
        System.out.printf("[VSTEAM-OMNI-JAVA] Member added: %s (%s)%n", name, role);
        return member;
    }

    public List<TeamMember> listMembers() {
        return new ArrayList<>(members.values());
    }

    // ---- Service Endpoint Management --------------------------------------

    public ServiceEndpoint addEndpoint(String name, String type, String url) {
        String id = nextId("ep");
        ServiceEndpoint ep = new ServiceEndpoint(id, name, type, url);
        endpoints.put(id, ep);
        System.out.printf("[VSTEAM-OMNI-JAVA] Endpoint added: %s (%s -> %s)%n", name, type, url);
        return ep;
    }

    // ---- VSTeam Drive (File-System-Like Navigation) -----------------------

    public DriveNode buildDriveTree() {
        DriveNode root = new DriveNode("Organization", "/", "organization");

        for (DevOpsProject proj : projects.values()) {
            DriveNode projNode = root.addChild(proj.name, "project");

            // Repos
            DriveNode reposNode = projNode.addChild("Repos", "area");
            for (GitRepository repo : gitRepos.values()) {
                if (repo.projectId.equals(proj.id)) {
                    reposNode.addChild(repo.name, "repository");
                }
            }

            // Pipelines
            DriveNode pipelinesNode = projNode.addChild("Pipelines", "area");
            for (BuildDefinition bd : buildDefs.values()) {
                if (bd.projectId.equals(proj.id)) {
                    pipelinesNode.addChild(bd.name, "build_definition");
                }
            }

            // Releases
            DriveNode releasesNode = projNode.addChild("Releases", "area");
            for (ReleaseDefinition rd : releaseDefs.values()) {
                if (rd.projectId.equals(proj.id)) {
                    releasesNode.addChild(rd.name, "release_definition");
                }
            }

            // Work items
            DriveNode workNode = projNode.addChild("Work Items", "area");
            for (WorkItem wi : workItems.values()) {
                if (wi.projectId.equals(proj.id)) {
                    workNode.addChild(wi.id + " " + wi.title, "work_item");
                }
            }
        }

        return root;
    }

    public List<String> navigateDrive(String path) {
        DriveNode root = buildDriveTree();
        String[] parts = path.split("/");
        DriveNode current = root;

        for (String part : parts) {
            if (part.isEmpty()) continue;
            boolean found = false;
            for (DriveNode child : current.children) {
                if (child.name.equalsIgnoreCase(part)) {
                    current = child;
                    found = true;
                    break;
                }
            }
            if (!found) return List.of("Path not found: " + path);
        }

        return current.listChildren();
    }

    // ---- Cross-Project Analytics ------------------------------------------

    public Map<String, Object> analytics() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("projects", projects.size());
        stats.put("build_definitions", buildDefs.size());
        stats.put("build_runs", buildRuns.size());
        stats.put("release_definitions", releaseDefs.size());
        stats.put("work_items_total", workItems.size());
        stats.put("work_items_active",
                workItems.values().stream().filter(wi -> wi.state == WorkItemState.ACTIVE).count());
        stats.put("repositories", gitRepos.size());
        stats.put("pull_requests_active",
                pullRequests.values().stream().filter(pr -> pr.status == PRStatus.ACTIVE).count());
        stats.put("team_members", members.size());
        stats.put("service_endpoints", endpoints.size());

        // Build success rate
        long completed = buildRuns.values().stream()
                .filter(b -> b.status == BuildStatus.COMPLETED).count();
        long succeeded = buildRuns.values().stream()
                .filter(b -> b.result == BuildResult.SUCCEEDED).count();
        stats.put("build_success_rate",
                completed > 0 ? String.format("%.1f%%", (double) succeeded / completed * 100) : "N/A");

        return stats;
    }

    public Map<String, Object> engineStats() {
        Map<String, Object> stats = analytics();
        stats.put("engine", "VSTeam DevOps Engine");
        stats.put("version", "1.0.0-omni");
        stats.put("organization_url", organizationUrl);
        return stats;
    }
}
