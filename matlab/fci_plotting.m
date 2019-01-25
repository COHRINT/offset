%% estimation error plots
num_agents = N;
sigma = 2;
state_num = 3;

% agent_plots_1 = [18 16 3 13 13 22];
% agent_plots_2 = [18 18 10 13 15 30];
% agent_plots_1 = [1 2 3 3 4 4];
% agent_plots_2 = [3 3 3 4 5 6];
agent_plots_1 = [1 2 3 4 4];
agent_plots_2 = [3 3 4 5 6];
% agent_plots_1 = [1 1 2 3 2];
% agent_plots_2 = [2 4 6 8 3];

color_wheel = [0    0.4470    0.7410;
    0.8500    0.3250    0.0980;
    0.9290    0.6940    0.1250;
    0.4940    0.1840    0.5560;
    0.4660    0.6740    0.1880;
    0.3010    0.7450    0.9330;
    0.6350    0.0780    0.1840];


figure
for i=1:length(agent_plots_1)
    
j = agent_plots_1(i);
k = agent_plots_2(i);

j_loc = find(sort([agents{k}.connections,agents{k}.agent_id]) == agent_plots_1(i));
k_loc = find(sort([agents{j}.connections,agents{j}.agent_id]) == agent_plots_2(i));



% if i>3
% figure
% end

subplot(2,3,i)
hold on; grid on;

set(gca,'FontSize',13)

if j~=k
    plot(input_tvec,agents{j}.local_filter.state_history(4*(k_loc-1)+state_num,:) - agents{k}.true_state(state_num,:),'Color',color_wheel(1,:))
    plot(input_tvec,sigma*sqrt(squeeze(agents{j}.local_filter.cov_history(4*(k_loc-1)+state_num,4*(k_loc-1)+state_num,:))),'Color',color_wheel(1,:),'LineStyle','--')
    plot(input_tvec,-sigma*sqrt(squeeze(agents{j}.local_filter.cov_history(4*(k_loc-1)+state_num,4*(k_loc-1)+state_num,:))),'Color',color_wheel(1,:),'LineStyle','--','HandleVisibility','off')
    % fill([input_tvec flip(input_tvec)],[2*sqrt(squeeze(agents{1}.local_filter.cov_history(4*(N-1)+1,4*(N-1)+1,:))'), 2*sqrt(squeeze(agents{N}.local_filter.cov_history(1,1,:))')],'g','LineStyle','none')
    % alpha(0.25)

%     str1 = strcat(num2str(j),'estimating',num2str(k));
%     str2 = strcat(num2str(k),'estimating',num2str(j));
%     legend(str1,strcat(num2str(sigma),'\sigma'),strcat('-',num2str(sigma),'\sigma'),str2,strcat(num2str(sigma),'\sigma'),strcat('-',num2str(sigma),'\sigma'),strcat('cent. KF ',num2str(j)),strcat('cent. KF ',num2str(k)))

    plot(input_tvec,agents{k}.local_filter.state_history((j_loc-1)*4+state_num,:)-agents{j}.true_state(state_num,:),'Color',[1 0 0])
    plot(input_tvec,sigma*sqrt(squeeze(agents{k}.local_filter.cov_history((j_loc-1)*4+state_num,(j_loc-1)*4+state_num,:))),'Color',[1 0 0],'LineStyle','--')
    plot(input_tvec,-sigma*sqrt(squeeze(agents{k}.local_filter.cov_history((j_loc-1)*4+state_num,(j_loc-1)*4+state_num,:))),'Color',[1 0 0],'LineStyle','--','HandleVisibility','off')
    % fill([input_tvec flip(input_tvec)],[2*sqrt(squeeze(agents{N}.local_filter.cov_history(1,1,:))'), -2*sqrt(squeeze(agents{N}.local_filter.cov_history(1,1,:))')],'r','LineStyle','none')
    % alpha(0.25)
    % plot(input_tvec,ci_time_vec,'x')

    plot(input_tvec,baseline_filter.state_history((j-1)*4+state_num,:)-agents{j}.true_state(state_num,:),'Color',color_wheel(5,:))
    plot(input_tvec,baseline_filter.state_history((k-1)*4+state_num,:)-agents{k}.true_state(state_num,:),'Color',color_wheel(3,:))
    % plot(input_tvec,2*sqrt(squeeze(baseline_filter.cov_history((j-1)*4+1,(j-1)*4+1,:))'),'k--')
    % plot(input_tvec,-2*sqrt(squeeze(baseline_filter.cov_history((j-1)*4+1,(j-1)*4+1,:))'),'k--')

    str1 = strcat(num2str(j),' estimating ',num2str(k));
    str2 = strcat(num2str(k),' estimating ',num2str(j));
%     legend(str1,strcat('\pm',num2str(sigma),'\sigma'),strcat('-',num2str(sigma),'\sigma'),str2,strcat(num2str(sigma),'\sigma'),strcat('-',num2str(sigma),'\sigma'),strcat('cent. KF  ',num2str(j)),strcat('cent. KF  ',num2str(k)))
    legend(str1,strcat('\pm',num2str(sigma),'\sigma'),str2,strcat('\pm',num2str(sigma),'\sigma'),strcat('cent. KF  ',num2str(j)),strcat('cent. KF  ',num2str(k)))
    xlabel('Time [s]')
    ylabel('Est Error [m]')
    title(['Estimation error in y pos, \delta=',num2str(delta),', ',num2str(j),'\leftrightarrow',num2str(k)])

else
    plot(input_tvec,agents{k}.local_filter.state_history((j_loc-1)*4+state_num,:)-agents{j}.true_state(state_num,:),'Color',[1 0 0])
    plot(input_tvec,sigma*sqrt(squeeze(agents{k}.local_filter.cov_history((j_loc-1)*4+state_num,(j_loc-1)*4+state_num,:))),'Color',[1 0 0],'LineStyle','--')
    plot(input_tvec,-sigma*sqrt(squeeze(agents{k}.local_filter.cov_history((j_loc-1)*4+state_num,(j_loc-1)*4+state_num,:))),'Color',[1 0 0],'LineStyle','--','HandleVisibility','off')
    % fill([input_tvec flip(input_tvec)],[2*sqrt(squeeze(agents{N}.local_filter.cov_history(1,1,:))'), -2*sqrt(squeeze(agents{N}.local_filter.cov_history(1,1,:))')],'r','LineStyle','none')
    % alpha(0.25)
    % plot(input_tvec,ci_time_vec,'x')

    plot(input_tvec,baseline_filter.state_history((j-1)*4+state_num,:)-agents{j}.true_state(state_num,:),'Color',color_wheel(5,:))
    % plot(input_tvec,2*sqrt(squeeze(baseline_filter.cov_history((j-1)*4+1,(j-1)*4+1,:))'),'k--')
    % plot(input_tvec,-2*sqrt(squeeze(baseline_filter.cov_history((j-1)*4+1,(j-1)*4+1,:))'),'k--')

    str1 = strcat(num2str(j),' estimating ',num2str(k));
    str2 = strcat(num2str(k),' estimating ',num2str(j));
    legend(str2,strcat('\pm',num2str(sigma),'\sigma'),strcat('cent. KF  ',num2str(j)))
    xlabel('Time [s]')
    ylabel('Est Error [m]')
    title(['Estimation error in y pos, \delta=',num2str(delta),', ',num2str(j),'\leftrightarrow',num2str(k)])
end

end