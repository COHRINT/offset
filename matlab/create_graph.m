% Create matlab graph from connection array
% 
% determine shortest path from each node to one of the specified target
% nodes

function [shortest_paths,g] = create_graph(connections,targets)

    % create graph vertex pair vectors
    conns = [];
    conns_sorted = [];

    % add verticies to pair vectors
    for i=1:length(connections) 
        for j = 1:length(connections{i})
            conns(:,end+1) = [i;connections{i}(j)];
%             end
        end
    end
    
    % determine unique vertex pairings
    for i=1:size(conns,2)
        unique_vec = 1;
        for j=1:size(conns_sorted,2)
            if all(sort(conns(:,i)) == sort(conns_sorted(:,j)))
                unique_vec = 0;
            end
        end
        if unique_vec
            conns_sorted(:,end+1) = conns(:,i);
        end
    end
    
    % divide vertex pairs into two vectors for matlab graph creation
    s = conns_sorted(1,:);
    t = conns_sorted(2,:);

    % create matlab graph object
    g = graph(s,t);
    
    shortest_paths = cell(1,length(connections));
    
    % find shortest path for each node to one of the target nodes
    for i=1:length(connections)
        sp = zeros(1,length(connections));
        for j=1:length(targets)
            if i ~= targets(j)
                sp_cand = g.shortestpath(i,targets(j));
                if length(sp_cand) < length(sp)
                    sp = sp_cand;
                end
            end
        end
        shortest_paths{i} = sp;
    end        
end