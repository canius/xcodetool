import os,glob,subprocess,argparse
import xml.etree.ElementTree as xt

__version__ = "0.0.1"

def getShcemesFromProject(project):
	pattern = os.path.join(project,"xcshareddata/xcschemes/*.xcscheme")
	return glob.glob(pattern)

def getShcemesFromWorkspace(workspace):
	schemes = []
	folder = os.path.dirname(workspace)
	projects = []
	root = xt.parse(os.path.join(workspace,"contents.xcworkspacedata"))
	for child in root.getroot():
		location = child.attrib['location'].split(':')[1]
		location = os.path.join(folder,location)
		projects.append(location)
	for project in projects:
		schemes.extend(getShcemesFromProject(project))
	return schemes

def getDataFromScheme(scheme):
	root = xt.parse(scheme)
	config = root.find("./ArchiveAction").attrib["buildConfiguration"]
	return config

def findSchemes(folder):
	workspaces = glob.glob(os.path.join(folder,"*.xcworkspace"))
	if len(workspaces) > 0:
		return (getShcemesFromWorkspace(workspaces[0]),workspaces[0])
	projects = glob.glob(os.path.join(folder,"*.xcodeproj"))
	if len(projects) > 0:
		return (getShcemesFromProject(projects[0]),projects[0])
	return []

def archiveAndExport(root_folder,output_folder,option_file,scheme,dsym):
	xcarchive_path = os.path.join(output_folder,scheme + ".xcarchive")
	scheme_path = ""
	scheme_paths,entry = findSchemes(root_folder)
	for s in scheme_paths:
		name = os.path.splitext(os.path.basename(s))[0]
		if scheme == name:
			scheme_path = s
			break
	if len(scheme_path) == 0:
		raise Exception("Cannot find workspace or project for the scheme")

	config = getDataFromScheme(scheme_path)

	cmd = ["xcodebuild"]
	cmd.append("-scheme")
	cmd.append(scheme)
	ext = os.path.splitext(os.path.basename(entry))[1]
	if ext == ".xcworkspace":
		cmd.append("-workspace")
	elif ext == ".xcodeproj":
		cmd.append("-project")
	else:
		raise Exception("Wrong entry type")
	cmd.append(entry)
	cmd.append('-configuration')
	cmd.append(config)
	cmd.append("clean")
	cmd.append("archive")
	cmd.append("-archivePath")
	cmd.append(xcarchive_path)
	cmd.append("-allowProvisioningUpdates")
	subprocess.call(cmd)

	cmd = ["xcodebuild"]
	cmd.append("-exportArchive")
	cmd.append("-archivePath")
	cmd.append(xcarchive_path)
	cmd.append("-exportPath")
	cmd.append(output_folder)
	cmd.append("-exportOptionsPlist")
	cmd.append(option_file)
	cmd.append("-allowProvisioningUpdates")
	subprocess.call(cmd)

	if dsym:
		cmd = ["ditto"]
		cmd.append("-c")
		cmd.append("-k")
		cmd.append("-rsrc")
		cmd.append(os.path.join(xcarchive_path,"dSYMs"))
		cmd.append(os.path.join(output_folder,"dSYMs.zip"))
		subprocess.call(cmd)

def integration(root_folder,scheme,sign_method):
	current = os.path.dirname(os.path.abspath(__file__))
	option_file = os.path.join(current,"options",sign_method + ".plist")
	output_folder = os.path.join(root_folder,"output")
	archiveAndExport(root_folder,output_folder,option_file,scheme,sign_method == "app-store" or sign_method == "enterprise")

def main():
	parser = argparse.ArgumentParser(description="xcodetool version {} , a convenient python tool for xcodebuild.".format(__version__))
	parser.add_argument("--scheme", type=str, help="the scheme to build and archive", required=True)
	parser.add_argument("--method", type=str, help="the sign method (ad-hoc|app-store|enterprise)", required=True)
	args = parser.parse_args()
	integration(os.getcwd(),args.scheme,args.method)

if __name__ == '__main__':
	main()
