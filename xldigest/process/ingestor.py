import os
import shutil
import uuid

from openpyxl import load_workbook

import xldigest.database.paths

from xldigest.database.models import RetainedSourceFile, ReturnItem, DatamapItem
from xldigest.process.exceptions import NoFilesInDirectoryError
from xldigest.process.template import BICCTemplate
from xldigest.process.datamap import Datamap
from xldigest.process.digest import Digest
from xldigest.database.connection import Connection


try:
    os.listdir(xldigest.database.paths.USER_DATA_DIR)
except FileNotFoundError:
    print("No data directory found at: {}".format(xldigest.database.paths.USER_DATA_DIR))
    print("Creating the directory now.")
    os.makedirs(xldigest.database.paths.USER_DATA_DIR)


# TODO
# There reasaon this class uses so many default params is because it's dual-
# -use at the moment as something, basically to allow for an Ingester to pick
# up all files in a source directory, or for pulling in a single populated
# template file. I suspect that the best option would be to get rid of the
# source_dir option and go for a single file Ingest.

# This probably needs to be handled with a class method that acts as an
# alternative init method.

class Ingestor:
    """
    The key class when importing a populated template containing data bound for
    the database.

    A path to the db file is required upon instantiation. The other arguments
    are optional. This allows it to operate on all files in a source directory
    by inclusion of Ingestor(source_dir=PATH), or for ingesting a single
    populated template file.
    """
    def __init__(self,
                 db_file: str,
                 source_dir: str=None,
                 portfolio_id: int=None,
                 series_item_id: int=None,
                 series_id: int=None,
                 project_id: int=None,
                 source_file: BICCTemplate=None) -> None:
        self.source_dir = source_dir
        self.project = project_id
        self.portfolio = portfolio_id
        self.series = series_id
        self.series_item = series_item_id
        self.source_file = source_file
        self.db_file = db_file

    def _non_duplicated_return(self) -> bool:
        """
        Returns True or False based on whether this combination of portfolio,
        project and series_item is already in the database.
        """
        session = Connection.session_with_file(self.db_file)
        data = session.query(RetainedSourceFile.portfolio_id,
                             RetainedSourceFile.project_id,
                             RetainedSourceFile.series_item_id).all()
        if (self.portfolio, self.project, self.series_item) in data:
            session.close()
            return False
        else:
            session.close()
            return True

    def import_single_return(self) -> None:
        """
        Import a single return in the form of a populated template and save it
        as ReturnItem values in the database.
        """
        session = Connection.session_with_file(self.db_file)
        datamap = Datamap(self.source_file, self.db_file)
        datamap.cell_map_from_database()
        digest = Digest(datamap, self.series_item, self.project)
        digest.read_template()
        for cell in digest.data:
#            cell_val_id = session.query(DatamapItem.id).filter(
#                DatamapItem.key == cell.cell_key).all()[0][0]

            return_item = ReturnItem(
                project_id=self.project,
                series_item_id=self.series_item,
                datamap_item_id=cell.datamap_id[0],
                value=cell.cell_value)
            print("Adding {}".format(return_item))
            session.add(return_item)
        session.commit()

    def write_source_file(self) -> str:
        """
        Writes the details of the self.source_file (which should be a populated
        tempalte file) to the database.

        Returns the path of where the source file is saved in the system after
        import.

        If returns an empty string, the source was not imported.
        """
        if self._non_duplicated_return():
            fuuid = str(uuid.uuid1())
            target_file_name = "_".join([
                str(self.portfolio),  # portfolio first field
                str(self.series_item),  # series_item second field
                str(self.project),  # project_third field
                fuuid, '.xlsx'])
            w_path = os.path.join(xldigest.database.paths.USER_DATA_DIR, target_file_name)
            self.import_single_return()
            # Here we write the file to our store
            shutil.copy(self.source_file.source_file, w_path)
            # Here we write the details to the db
            session = Connection.session_with_file(self.db_file)
            retained_f = RetainedSourceFile(
                project_id=self.project,
                portfolio_id=self.portfolio,
                series_item_id=self.series_item,
                uuid=fuuid)
            session.add(retained_f)


            session.commit()
            session.close()
            return w_path
        else:
            return ""

    def source_xls_only(self) -> bool:
        """
        Tests whether there are only xlsx files in a Ingestor.source_dir.
        """
        fls = os.listdir(self.source_dir)
        if len(fls) > 0:
            for f in fls:
                try:
                    load_workbook(self.source_dir + '/' + f)
                except:
                    print("{} - that's not an xlsx file".format(f))
                    return False
            return True
        else:
            raise NoFilesInDirectoryError

    def __repr__(self):
        return "Ingestor()"

    def __str__(self):
        return "Ingestor()"
