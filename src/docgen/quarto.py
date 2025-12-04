import subprocess
import sys
import logging
from docgen.settings import settings
import requests
import zipfile
import shutil
from tqdm import tqdm
import semver

logger = logging.getLogger(__name__)

def run(cmd:list|tuple, **kwargs):
    """
    Exécute quarto local en utilisant subprocess.run.
    """
    assert isinstance(cmd, (list, tuple)), "cmd doit être une liste ou un tuple"
    logger.debug(f"Exécution de la commande Quarto : {cmd}, kwargs={kwargs}")
    return subprocess.run([str(settings.local_quarto_exe),*cmd], **kwargs)


def register_kernel():
    """
    Enregistre le kernel Jupyter sous le nom 'docgen_env' pour Quarto.
    """
    try:
        subprocess.run([
            sys.executable, "-m", "ipykernel", "install",
            "--user", "--name", settings.ipykernel_name,
        ], check=True)
        logger.info(f"Kernel Jupyter enregistré : {settings.ipykernel_name}")
    except subprocess.CalledProcessError as e:
        logger.exception("Échec de l'enregistrement du kernel Jupyter : %s", e)


def _extract_zip(archive_path):
    """Extrait une archive ZIP."""
    import zipfile
    
    logger.info("Extraction de l'archive ZIP de Quarto...")
    extract_path = settings.local_quarto_path.with_name(settings.local_quarto_path.name + "_tmp")
    
    # Nettoyer le répertoire d'extraction s'il existe
    if extract_path.exists():
        shutil.rmtree(extract_path)
    extract_path.mkdir(parents=True, exist_ok=True)
    
    # Extraire l'archive avec barre de progression
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        members = zip_ref.infolist()
        with tqdm(desc="Extraction", total=len(members), unit="fichier") as extract_bar:
            for member in members:
                zip_ref.extract(member, extract_path)
                extract_bar.update(1)
    
    _finalize_extraction(extract_path)

def _extract_tarball(archive_path):
    """Extrait une archive TAR (tar.gz, tgz, tar)."""
    import tarfile
    
    logger.info("Extraction de l'archive TAR de Quarto...")
    extract_path = settings.local_quarto_path.with_name(settings.local_quarto_path.name + "_tmp")
    
    # Nettoyer le répertoire d'extraction s'il existe
    if extract_path.exists():
        shutil.rmtree(extract_path)
    extract_path.mkdir(parents=True, exist_ok=True)
    
    # Extraire l'archive avec barre de progression
    with tarfile.open(archive_path, 'r:*') as tar_ref:
        members = tar_ref.getmembers()
        with tqdm(desc="Extraction", total=len(members), unit="fichier") as extract_bar:
            for member in members:
                tar_ref.extract(member, extract_path)
                extract_bar.update(1)
    
    _finalize_extraction(extract_path)


def _finalize_extraction(extract_path):
    """Finalise l'extraction en déplaçant les fichiers."""
    # Nettoyer le répertoire d'installation s'il existe
    if settings.local_quarto_path.exists():
        shutil.rmtree(settings.local_quarto_path)
    
    # Trouver le dossier racine extrait (souvent quarto-x.x.x)
    extracted_items = list(extract_path.iterdir())
    extracted_dirs = [d for d in extracted_items if d.is_dir()]
    
    found = False
    if len(extracted_dirs) == 1:
        # Si un seul dossier, commençant par quarto-x.x.x => le déplacer vers le chemin final
        source_folder = extracted_dirs[0]
        name = source_folder.name
        demanded_name = settings.local_quarto_path.name
        found = demanded_name.startswith(name)
        if found:
            shutil.move(str(source_folder), str(settings.local_quarto_path))
    
    if not found and len(extracted_items) > 0:
        # Sinon, créer le dossier cible et déplacer tout le contenu
        settings.local_quarto_path.mkdir(parents=True, exist_ok=True)
        for item in extracted_items:
            dest = settings.local_quarto_path / item.name
            shutil.move(str(item), str(dest))
    elif not found:
        logger.error("Aucun fichier trouvé dans l'archive extraite")
        return
    
    # Rendre l'exécutable exécutable sur Unix
    if not sys.platform.startswith("win"):
        import stat
        if settings.local_quarto_exe.exists():
            settings.local_quarto_exe.chmod(
                settings.local_quarto_exe.stat().st_mode | stat.S_IEXEC
            )

     # Nettoyer le répertoire d'extraction s'il existe
    if extract_path.exists():
        shutil.rmtree(extract_path)
    
    logger.info("Installation de Quarto terminée.")

def install_quarto():
    """
    Télécharge et installe Quarto depuis l'URL de téléchargement configurée.
    Supporte le format ZIP.
    """
    try:
        # Nom du fichier à partir de l'URL
        filename = settings.quarto_download_url.split("/")[-1]
        local_file_path = settings.local_quarto_path.parent / filename
        
        if not local_file_path.exists():
            logger.info(f"Téléchargement de Quarto depuis : {settings.quarto_download_url}")
            
            # Télécharger le fichier
            response = requests.get(settings.quarto_download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))

            # Enregistrer le fichier localement
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_file_path, 'wb') as file, tqdm(
                desc=f"Téléchargement {filename}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Vérifier que le chunk n'est pas vide
                        file.write(chunk)
                        progress_bar.update(len(chunk))
                
            logger.info(f"Quarto téléchargé et enregistré sous : {local_file_path}")
        else:
            logger.info(f"Quarto déjà téléchargé et enregistré sous : {local_file_path}")
        
                # Traitement selon le type de fichier
        if filename.endswith('.zip'):
            _extract_zip(local_file_path)
        elif filename.endswith(('.tar.gz', '.tgz', '.tar')):
            _extract_tarball(local_file_path)
        else:
            logger.warning(f"Format de fichier non supporté : {filename}")
            logger.info("Fichier téléchargé mais non installé automatiquement")
        
        
    except requests.RequestException as e:
        logger.exception("Erreur lors du téléchargement de Quarto : %s", e)
        raise
    except subprocess.CalledProcessError as e:
        logger.exception("Erreur lors de l'installation de Quarto : %s", e)
        raise
    except zipfile.BadZipFile as e:
        logger.exception("Erreur lors de l'extraction de l'archive ZIP : %s", e)
        raise
    except Exception as e:
        logger.exception("Erreur générale lors de l'installation de Quarto : %s", e)
        raise

def verify_quarto(install:bool = True):
    """
    Vérifie que l’exécutable 'quarto' est disponible.
    """
    try:
        run(["--version"], check=True, stdout=subprocess.DEVNULL)
        logger.info("Quarto est installé.")
    except FileNotFoundError:
        if install:
            install_quarto()
            return verify_quarto(False)
        logger.error("Quarto n’est pas installé ou introuvable dans le PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.exception("Erreur lors de la vérification de Quarto : %s", e)
        sys.exit(1)


def install_tinytex():
    """
    Installe TinyTeX via Quarto pour la génération de PDF.
    """
    try:
        run(["install", "tinytex"], check=True)
        logger.info("TinyTeX installé via Quarto.")
    except subprocess.CalledProcessError as e:
        logger.exception("Échec de l'installation de TinyTeX : %s", e)


def install():
    """
    Lance le déploiement complet : kernel Jupyter, Quarto, TinyTeX.
    """
    logger.info(f"Python utilisé : {sys.executable}")
    register_kernel()
    verify_quarto()
    install_tinytex()
    logger.info("Déploiement terminé.")

def install_once():
    p = settings.dynotec_home / ".last_install"
    version = "0.0.0"
    if p.exists():
        with open(p, 'r') as f:
            version = f.read().strip()

    if semver.compare(settings.package_version, version) > 0 or not settings.local_quarto_exe.exists():
        logger.info(f"Version actuelle : {version}, mise à jour vers {settings.package_version}")    
        install()
        with open(p, 'w') as f:
            f.write(settings.package_version)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # verify_quarto()
    run(["--version"])