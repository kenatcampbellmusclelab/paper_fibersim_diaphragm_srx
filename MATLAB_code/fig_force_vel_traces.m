function fig_force_pCa
% Makes force-pCa figure

% Variables
sim_dir = '../simulations/a/permeabilized/sim_data/fv_pCa45/isotonic/sim_output';
n_cond = 3;

output_file_string = '../output/fig_force_pCa';
output_file_string_traces = '../output/fig_force_vel_traces'
output_types = {'png', 'eps', 'svg'};

f_scaling_factor = 0.001;
y_traces_label_offset = -0.5;
y_label_offset = -0.22;
table_font_size = 8;
marker_size = 6;
marker_symbols = {'o','o','o'};
marker_edge_colors = zeros(3,3);
marker_face_colors = [0 0.7 0 ; 0.3 0.3 0.3 ; 0.7 0 0];
leg_strings = {'Control', 'Crit', {'Crit+','drug'}};

title_y_offset = -1.3;

t_ticks = [0.95 1.3]
f_ticks = [0 80]

y_ticks = [8 4.5 ; f_ticks ; 700 1100 ; 0 1 ; 0 1];
y_tick_dp = [1 0 0 1 1]

y_label_strings = {{'pCa'}, ...
                    {'Force', 'normalized to', 'area', '(kN m^{-2})'}, ...
                    {'Half-', 'sarcomere', 'length', '(nm)'}, ...
                    {'Thin', 'filament'}, ...
                    {'Thick', 'filament'}};

thin_strings = {'Inactive', 'Active'};
thick_strings = {'SRX', 'DRX', 'Attached'};

sim_line_width = 1.2;

state_hex_colors = ['#1f77b4' ; '#ff7f0e' ; '#8c564b'];
state_colors = hex2rgb(state_hex_colors)


% Make the figure
figure(1);
clf

n_cols = 3;
n_rows = 5;

sp = initialise_publication_quality_figure( ...
        'no_of_panels_wide', n_cols, ...
        'no_of_panels_high', n_rows, ...
        'right_margin', 0.5, ...
        'left_pads', repmat([1.2, 0.2, 0.2], [1 n_rows]), ...
        'right_pads', repmat([0.2 0.2 1.2], [1 n_rows]), ...
        'individual_padding', 1, ...
        'axes_padding_top', 0.1, ...
        'axes_padding_bottom', 0.2, ...
        'top_margin', 0.4, ...
        'bottom_margin', 0.35, ...
        'x_to_y_axes_ratio', 2, ...
        'panel_label_font_size', 0);

% Cycle through data folders
for i = 1 : n_cond
    cond_dir = fullfile(sim_dir, sprintf('%i', i));
    cond_files = findfiles('txt', cond_dir, 0)';

    % Cut out the rates file
    cond_files(startsWith(cond_files,'rates')) = [];

    for j = 1 : numel(cond_files)
        d = readtable(cond_files{j});

        ti = find((d.time > t_ticks(1)) & ...
                (d.time < t_ticks(end)));
        d = d(ti,:);

        plot_index = i;
        subplot(sp(plot_index));
        hold on;
        d.pCa(d.pCa >= 8) = 8;
        plot(d.time, d.pCa, 'k-', ...
                'LineWidth', 1);

        plot_index = plot_index + n_cols;
        subplot(sp(plot_index));
        hold on;
        f = f_scaling_factor * d.force;
        plot(d.time, f, '-', ...
            'Color', marker_face_colors(i,:), ...
                'LineWidth', sim_line_width);

        peak_force(i,j) = max(f);

        plot_index = plot_index + n_cols;
        subplot(sp(plot_index));
        hold on;
        plot(d.time, d.hs_length, '-', ...
            'Color', marker_face_colors(i,:), ...
                'LineWidth', sim_line_width);

        plot_index = plot_index + n_cols;
        subplot(sp(plot_index));
        hold on;
        for k = 1 : 2
            field_string = sprintf('a_pop_%i', k-1);
            h_a(k) = plot(d.time, d.(field_string), '-', ...
                'Color', state_colors(k,:), ...
                'LineWidth', sim_line_width);
        end

        plot_index = plot_index + n_cols;
        subplot(sp(plot_index));
        hold on;
        for k = 1 : 3
            field_string = sprintf('m_pop_%i', k-1);
            h_m(k) = plot(d.time, d.(field_string), '-', ...
                'Color', state_colors(k,:), ...
                'LineWidth', sim_line_width);
        end

    end
end

% Labels
for i = 1 : n_cols
    for j = 1 : n_rows
        plot_index = i + (j-1) * n_cols;

        if (j==1)
            title_string = leg_strings{i};
        else
            title_string = '';
        end
        
        subplot(sp(plot_index));
        improve_axes( ...
            'x_ticks', t_ticks, ...
            'x_axis_off', ~isequal(j, n_rows), ...
            'x_tick_decimal_places', 1, ...
            'x_axis_label', 'Time (s)', ...
            'y_ticks', y_ticks(j,:), ...
            'y_axis_off', ~isequal(i,1), ...
            'y_tick_decimal_places', y_tick_dp(j), ...
            'y_axis_label', y_label_strings{j}, ...
            'y_label_offset', y_traces_label_offset, ...
            'title', title_string, ...
            'title_y_offset', title_y_offset);
    end
end

subplot(sp(9))
legendflex(h_a, thin_strings, ...
    'xscale', 0.5, ...
    'FontSize', 8, ...
    'padding', [2 2 2], ...
    'anchor', {'se', 'sw'}, ...
    'buffer', [10, 5]);

subplot(sp(12))
legendflex(h_m, thick_strings, ...
    'xscale', 0.5, ...
    'FontSize', 8, ...
    'padding', [2 2 2], ...
    'anchor', {'se', 'sw'}, ...
    'buffer', [10, 5]);

for i = 1 : numel(output_types)
    figure_export('output_file_string', output_file_string_traces, ...
        'output_type', output_types{i});
end

% 
% 
% % Cycle through data folders
% for i = 1 : n_cond
%     cond_dir = fullfile(sim_dir, sprintf('%i', i));
%     cond_files = findfiles('txt', cond_dir, 0);
% 
%     for j = 1 : numel(cond_files)
%         sim_data = readtable(cond_files{j});
%         pd(i).pCa(j) = sim_data.pCa(end);
%         pd(i).y(j) = f_scaling_factor * sim_data.force(end);
%         pd(i).y_error(j) = 0;
%     end
% 
%     [pd(i).pCa50, pd(i).n_H, ~, ~, ~, pd(i).x_fit, pd(i).y_fit] = ...
%         fit_Hill_curve(pd(i).pCa, pd(i).y);
% end
% 
% % Make the figure
% figure(1);
% clf
% 
% sp = initialise_publication_quality_figure( ...
%         'no_of_panels_wide', 1, ...
%         'no_of_panels_high', 1, ...
%         'axes_padding_left', 0.9, ...
%         'axes_padding_right', 0.2, ...
%         'top_margin', 0, ...
%         'bottom_margin', 0, ...
%         'panel_label_font_size', 0);
% 
% [h,ad] = plot_pCa_data_with_y_errors(pd, ...
%             'high_pCa_value', 8, ...
%             'y_axis_label', {'Force','normalized','to area', '(kN m^{-2})'}, ...
%             'y_label_offset', y_label_offset, ...
%             'marker_size', marker_size, ...
%             'marker_symbols', marker_symbols, ...
%             'marker_face_colors', marker_face_colors, ...
%             'marker_edge_colors', marker_edge_colors, ...
%             'x_ticks', [7 6.5:-0.5:4]);
% 
% % Add in table
% xt = 5.3 - cumsum([0 0.38 0.32 0.4]);
% yt = linspace(42, 10, 4);
% for i = 1 : numel(xt)
%     for j = 1 : numel(yt)
%         t_text_strings{j, i} = '';
%         t_marker_symbols{j, i} = '';
%         t_marker_face_colors(j, i, :) = [0 0 0];
%         t_marker_edge_colors(j, i, :) = [0 0 0];
%         t_marker_sizes(j, i) = 0;
%     end
% end
% 
% t_text_strings{1,3} = 'pCa_{50}';
% t_text_strings{1,4} = 'n_H';
% for i = 1 : n_cond
%     t_text_strings{(i+1), 1} = leg_strings{i};
%     t_text_strings{(i+1), 3} = sprintf('%.2f', pd(i).pCa50);
%     t_text_strings{(i+1), 4} = sprintf('%.2f', pd(i).n_H);
% end
% for i = 1 : n_cond
%     t_marker_symbols{(i+1), 2} = h(i).Marker;
%     t_marker_edge_colors((i+1), 2, :) = h(i).MarkerEdgeColor;
%     t_marker_face_colors((i+1), 2, :) = h(i).MarkerFaceColor;
%     t_marker_sizes((i+1), 2) = h(i).MarkerSize;
% end
% 
% plot_table(...
%     'x', xt, ...
%     'y', yt, ...
%     'text_strings', t_text_strings, ...
%     'marker_symbols', t_marker_symbols, ...
%     'marker_face_color', t_marker_face_colors, ...
%     'marker_sizes', t_marker_sizes, ...
%     'font_size', table_font_size, ...
%     'border_color', 'k', ...
%     'border_dx', [0.27 -0.2], ...
%     'border_dy', [3 -8]);
% 
% 
% for i = 1 : numel(output_types)
%     figure_export('output_file_string', output_file_string, ...
%         'output_type', output_types{i});
% end