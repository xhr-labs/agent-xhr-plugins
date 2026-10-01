#  TechDocs


    ## What is this?

    This is a placeholder TechDocs page. Here you will write your technical documentation for your software. This supports markdown, so get styling!

    ## Some Cool Features

    ### Mermaid Diagrams

    ```mermaid
    %%{init: {'theme': 'forest'}}%%
    graph LR
    A[Start] --> B{Error?};
    B -->|Yes| C[Hmm...];
    C --> D[Debug];
    D --> B;
    B ---->|No| E[Yay!];
    ```

    ### Graphviz Graphs
    
    ```dot
    digraph G {
        rankdir=LR
        Earth [peripheries=2]
        Mars
        Earth -> Mars
    }
    ```

    ### Additional Reading

    - [MKDocs: Writing your docs](https://www.mkdocs.org/user-guide/writing-your-docs/)
    - [Python Markdown](https://python-markdown.github.io/)

