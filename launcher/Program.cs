using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;

namespace AIStoryStudio.Launcher;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();
        Application.Run(new LauncherForm());
    }
}

internal sealed class LauncherForm : Form
{
    private readonly Label status = new() { AutoSize = true, ForeColor = Color.DimGray };
    private readonly Button launchButton = new() { Text = "Iniciar AI Story Studio", AutoSize = true };
    private readonly Button openButton = new() { Text = "Abrir aplicación", AutoSize = true, Enabled = false };
    private readonly Button stopButton = new() { Text = "Detener servicios", AutoSize = true, Enabled = false };
    private Process? process;

    public LauncherForm()
    {
        Text = "AI Story Studio";
        ClientSize = new Size(420, 185);
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        StartPosition = FormStartPosition.CenterScreen;

        var title = new Label
        {
            Text = "AI Story Studio",
            Font = new Font(Font.FontFamily, 18, FontStyle.Bold),
            AutoSize = true,
            Location = new Point(24, 22),
        };
        var description = new Label
        {
            Text = "Inicia la aplicación local y abre el navegador automáticamente.",
            AutoSize = true,
            Location = new Point(26, 58),
        };
        status.Location = new Point(26, 88);
        status.Text = "Listo para iniciar.";
        launchButton.Location = new Point(26, 122);
        openButton.Location = new Point(188, 122);
        stopButton.Location = new Point(297, 122);

        launchButton.Click += (_, _) => StartApplication();
        openButton.Click += (_, _) => Process.Start(new ProcessStartInfo("http://localhost:5173") { UseShellExecute = true });
        stopButton.Click += (_, _) => StopApplication();
        FormClosing += (_, _) => StopApplication();

        Controls.AddRange([title, description, status, launchButton, openButton, stopButton]);
    }

    private void StartApplication()
    {
        if (process is { HasExited: false }) return;

        var root = AppContext.BaseDirectory;
        var script = Path.Combine(root, "start.ps1");
        if (!File.Exists(script))
        {
            MessageBox.Show("No se encontró start.ps1. Coloca el ejecutable en la carpeta principal del proyecto.",
                "AI Story Studio", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return;
        }

        try
        {
            process = Process.Start(new ProcessStartInfo
            {
                FileName = "powershell.exe",
                Arguments = $"-NoProfile -ExecutionPolicy Bypass -File \"{script}\"",
                WorkingDirectory = root,
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Normal,
            });
            status.Text = "Iniciando servicios…";
            launchButton.Enabled = false;
            openButton.Enabled = true;
            stopButton.Enabled = true;
        }
        catch (Exception exception)
        {
            MessageBox.Show(exception.Message, "No se pudo iniciar", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void StopApplication()
    {
        if (process is { HasExited: false })
        {
            process.Kill(entireProcessTree: true);
            process.Dispose();
        }
        process = null;
        status.Text = "Servicios detenidos.";
        launchButton.Enabled = true;
        openButton.Enabled = false;
        stopButton.Enabled = false;
    }
}
