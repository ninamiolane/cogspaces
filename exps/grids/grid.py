import sys

from joblib import Parallel, delayed
from os.path import join
from sklearn.model_selection import ParameterGrid
from sklearn.utils import check_random_state

from cogspaces.datasets.utils import get_data_dir, get_output_dir
from cogspaces.utils.sacred import get_id, OurFileStorageObserver
from exps.train import exp


@exp.config
def base():
    seed = 0
    data = dict(
        source_dir=join(get_data_dir(), 'reduced_512'),
        studies=['hcp']
    )


def variational():
    seed = 1
    system = dict(
        device=-1,
        verbose=0,
    )
    data = dict(
        source_dir=join(get_data_dir(), 'reduced_512'),
        studies='all',
        target_study='archi'
    )
    model = dict(
        normalize=False,
        estimator='factored_variational',
        study_weight='sqrt_sample',
        max_iter=100,
    )
    factored_variational = dict(
        optimizer='adam',
        latent_size=128,
        activation='linear',
        epoch_counting='all',
        sampling='random',
        batch_size=128,
        dropout=0.75,
        l1_penalty=0,
        lr=1e-3,
        input_dropout=0.25,)


def run_exp(output_dir, config_updates, _id, mock=False):
    """Boiler plate function that has to be put in every multiple
        experiment script, as exp does not pickle."""
    if not mock:
        observer = OurFileStorageObserver.create(basedir=output_dir)

        run = exp._create_run(config_updates=config_updates, )
        run._id = _id
        run.observers.append(observer)
        run()
    else:
        exp.run_command('print_config', config_updates=config_updates, )


if __name__ == '__main__':
    grid = sys.argv[1]
    if grid == 'variational':
        output_dir = join(get_output_dir(), 'variational_2')
        exp.config(variational)
        seeds = check_random_state(1).randint(0, 100000, size=4)
        config_updates = ParameterGrid({'seed': seeds,
                                        'factored_variational.embedder_reg':
                                            [1., 3., 4., 5., 10.]})
    else:
        raise ValueError('Wrong argument')

    _id = get_id(output_dir)
    Parallel(n_jobs=20, verbose=100)(delayed(run_exp)(output_dir,
                                                      config_update,
                                                      mock=False,
                                                      _id=_id + i)
                                     for i, config_update
                                     in enumerate(config_updates))
