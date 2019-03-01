% FUSION paper mse plots

% assumes network_mse matrix in workspace

% plot general info, indep of network config
% figure
% subplot(3,1,1)
% hold on; grid on;
% for i=1:size(avg_mse,1)
%     plot(input_tvec,avg_mse(i,:))
% end
% title('Avg per agent position MSE')
% xlabel('Time [s]')
% ylabel('MSE [m^2]')
% 
% subplot(3,1,2)
% hold on; grid on;
% for i=1:size(avg_xmse,1)
%     plot(input_tvec,avg_xmse(i,:))
% end
% title('Avg per agent x position MSE')
% xlabel('Time [s]')
% ylabel('MSE [m^2]')
% 
% subplot(3,1,3)
% hold on; grid on;
% for i=1:size(avg_ymse,1)
%     plot(input_tvec,avg_ymse(i,:))
% end
% title('Avg per agent y position MSE')
% xlabel('Time [s]')
% ylabel('MSE [m^2]')


figure
hold on; grid on;
plot(input_tvec,network_mse(1,:,1))
title('Agent 1 position MSE')
xlabel('Time [s]')
ylabel('MSE [m^2]')

figure
hold on; grid on;
plot(input_tvec,network_mse(10,:,1))
title('Agent 2 position MSE')

figure
hold on; grid on;
plot(input_tvec,network_mse(17,:,1))
title('Agent 3 position MSE')

% figure
% subplot(2,1,1)
% heatmap(network_mse(1,:,1))
% title('Network position MSE')
% xlabel('Time')
% ylabel('Agent')
% 
% subplot(2,1,2)
% heatmap(network_mse(:,:,1))
% title('Network position MSE')
% xlabel('Time')
% ylabel('Agent')