# Allows action if actor has permission
allow(actor, action, resource) if
    has_permission(actor, action, resource);

# Super users are allowed to do everything
allow(user: User, _action, _resource) if
    user.is_superuser = true;

# Generic role assignment
has_role(user: User, name: String, project: Project) if
    role in user.project_roles and
    role.role = name and
    role.project = project;

# Handle public objects
has_role(_user: User, "guest", project: Project) if
    project.public = true;

has_role(_user: User, "guest", model: Model) if
    model.public = true;

has_role(_user: User, "guest", schema: Schema) if
    schema.public = true;

# Handle verified required for creation
has_role(user: User, "verified", _project: Project) if
    user.verified = true;

has_role(user: User, "verified", _model: Model) if
    user.verified = true;

has_role(user: User, "verified", _schema: Schema) if
    user.verified = true;

actor User {
    permissions = ["get", "create", "delete"];
    roles = ["guest", "maintainer", "admin"];
    relations = { roleProject: RoleProject, roleModel: RoleModel};

    # admin permissions (only available for superuser)
    "get" if "admin";
    "create" if "admin";
    "delete" if "admin";
}

resource RoleProject {
    permissions = ["get", "create", "delete", "patch"];
    roles = ["guest", "maintainer", "admin"];
    relations = { project: Project };

    # admin permissions
    "get" if "admin";
    "create" if "admin";
    "delete" if "admin";
    "patch" if "admin";

    # role inheritance via project
    "guest" if "guest" on "project";
    "maintainer" if "maintainer" on "project";
    "admin" if "admin" on "project";
}

resource RoleModel {
    permissions = ["get", "create", "delete", "patch"];
    roles = ["guest", "maintainer", "admin"];
    relations = { model: Model };

    # admin permissions
    "get" if "admin";
    "create" if "admin";
    "delete" if "admin";
    "patch" if "admin";

    # role inheritance via model
    "guest" if "guest" on "model";
    "maintainer" if "maintainer" on "model";
    "admin" if "admin" on "model";
}

resource Project {
    permissions = ["get", "create", "delete", "patch", "create_roles", "modify_graph"];
    roles = ["guest", "maintainer", "admin"];

    # guest permissions
    "get" if "guest";

    # maintainer permissions
    "modify_graph" if "maintainer";
    "patch" if "maintainer";

    # admin permissions
    "delete" if "admin";
    "create_roles" if "admin";
    
    # role inheritance
    "guest" if "maintainer";
    "maintainer" if "admin";
}

resource Model {
    permissions = ["get", "create", "delete", "patch", "create_roles", "modify_graph", "create_datasource", "create_file", "create_schema"];
    roles = ["guest", "maintainer", "admin"];

    # guest permissions
    "get" if "guest";

    # maintainer permissions
    "patch" if "maintainer";
    "modify_graph" if "maintainer";
    "create_datasource" if "maintainer";
    "create_file" if "maintainer";
    "create_schema" if "maintainer";

    # admin permissions
    "delete" if "admin";
    "create_roles" if "admin";

    # role inheritance
    "guest" if "maintainer";
    "maintainer" if "admin";
}

resource DataSource {
    permissions = ["query", "stats", "delete", "patch", "insert_data", "modify_mapping"];
    roles = ["guest", "maintainer", "admin"];
    relations = { model: Model };

    # guest permissions
    "query" if "guest";
    "stats" if "guest";

    # maintainer permissions
    "patch" if "maintainer";
    "insert_data" if "maintainer";
    "modify_mapping" if "maintainer";

    # admin permissions
    "delete" if "admin";

    # role inheritance via model
    "guest" if "guest" on "model";
    "maintainer" if "maintainer" on "model";
    "admin" if "admin" on "model";
}

resource Schema {
    permissions = ["get", "create", "delete", "patch"];
    roles = ["guest", "maintainer", "admin"];
    relations = { model: Model };

    # guest permissions
    "get" if "guest";

    # admin permissions
    "patch" if "admin";
    "delete" if "admin";

    # role inheritance
    "guest" if "guest" on "model";
    "maintainer" if "maintainer" on "model";
    "admin" if "admin" on "model";
}

resource FileObject {
    permissions = ["get", "delete", "patch"];
    roles = ["guest", "maintainer", "admin"];
    relations = { model: Model };

    # guest permissions
    "get" if "guest";

    # admin permissions
    "delete" if "admin";
    "patch" if "admin";

    # role inheritance via model
    "guest" if "guest" on "model";
    "maintainer" if "maintainer" on "model";
    "admin" if "admin" on "model";
}


# Relate FileObject to Model
has_relation(model: Model, "model", file_object: FileObject) if
    file_object.model = model;

# Relate Datasource to Model
has_relation(model: Model, "model", datasource: DataSource) if
    datasource.model = model;

# Relate Schema to Model
has_relation(model: Model, "model", schema: Schema) if
    schema.model = model;

# Relate Project to RoleProject
has_relation(project: Project, "project", role: RoleProject) if
    role.project = project;

# Relate Model to RoleModel
has_relation(model: Model, "model", role: RoleModel) if
    role.model = model;

# Relate User to ProjectRole
has_relation(role: RoleProject, "roleProject", user: User) if
    role.user = user;

# Relate User to ModelRole
has_relation(role: RoleModel, "roleModel", user: User) if
    role.user = user;